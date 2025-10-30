import os, io, sys, time, glob
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
from tqdm import tqdm

import torch
from transformers import AutoModel, AutoTokenizer

# ================== Réglages ==================
MODEL_NAME = "deepseek-ai/DeepSeek-OCR"
PROMPT     = "<image>\n<|grounding|>Convert the document to text."
# Bon compromis VRAM/qualité (style "Gundam")
BASE_SIZE  = 1024
IMAGE_SIZE = 640
CROP_MODE  = True

DPI       = 144                  # rendu PDF -> image
DTYPE_TRY = ("bfloat16","float16")
ATTN_IMPL = "eager"              # pour windows mais à changer puor le mac
READ_BACK_EXTS = (".md", ".mmd", ".txt")
# ==============================================

def load_model():
    tok = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        use_safetensors=True,
        attn_implementation=ATTN_IMPL,  # DeepSeek-OCR ne supporte pas SDPA ici
    ).eval()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA non disponible (GPU requis).")

    model = model.cuda()
    for dt in DTYPE_TRY:
        try:
            model = model.to(getattr(torch, dt))
            break
        except Exception:
            continue
    return tok, model

def pdf_to_images(pdf_path: str, dpi: int = 144):
    """Rend chaque page du PDF en image PIL RGB."""
    Image.MAX_IMAGE_PIXELS = None
    doc = fitz.open(pdf_path)
    images = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for p in doc:
        pix = p.get_pixmap(matrix=mat, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)
    doc.close()
    return images

def newest_written_file(folder: Path, since_ts: float):
    """Retourne le fichier le plus récent (.md/.mmd/.txt) écrit après since_ts."""
    candidates = []
    for ext in READ_BACK_EXTS:
        candidates.extend(glob.glob(str(folder / f"*{ext}")))
    newest = None
    newest_mtime = since_ts
    for path in candidates:
        try:
            mtime = os.path.getmtime(path)
            if mtime >= newest_mtime:
                newest = path
                newest_mtime = mtime
        except FileNotFoundError:
            pass
    return newest

def extract_pdf_to_text(pdf_path: str, out_dir: str):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "images").mkdir(exist_ok=True)

    print("Loading model...")
    tok, model = load_model()

    print("Rendering PDF pages to images...")
    pages = pdf_to_images(pdf_path, dpi=DPI)

    tmp_dir = out_dir / "_tmp_pages"
    tmp_dir.mkdir(exist_ok=True)

    md_parts = []
    for i, pil_img in enumerate(tqdm(pages, desc="OCR pages")):
        page_path = tmp_dir / f"page_{i:04d}.jpg"
        pil_img.save(page_path, format="JPEG", quality=92)

        # On enregistre l'heure avant d'appeler infer pour retrouver le bon fichier.
        t0 = time.time()

        # IMPORTANT: save_results=True (sinon infer peut renvoyer None)
        res = model.infer(
            tok,
            prompt=PROMPT,
            image_file=str(page_path),
            output_path=str(out_dir),
            base_size=BASE_SIZE,
            image_size=IMAGE_SIZE,
            crop_mode=CROP_MODE,
            save_results=True,
            test_compress=True
        )

        # Cas où infer renvoie du texte exploitable
        text = None
        if isinstance(res, dict):
            # certaines versions renvoient {"text": "..."} ou {"output": "..."}
            text = res.get("text") or res.get("output")

        # Sinon, on relit le dernier fichier généré dans out_dir
        if not text or not str(text).strip():
            newest = newest_written_file(out_dir, since_ts=t0 - 0.5)
            if newest:
                try:
                    text = Path(newest).read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    text = Path(newest).read_text(encoding="utf-8", errors="ignore")

        if not text or not str(text).strip():
            text = ""  # évite "None" dans le markdown

        # nettoyage léger + séparateur de pages
        text = text.replace("<｜end▁of▁sentence｜>", "")
        md_parts.append(text.strip() + "\n\n<--- Page Split --->\n")

    md_path = out_dir / (Path(pdf_path).stem + ".md")
    md_path.write_text("".join(md_parts), encoding="utf-8")

    print(f"\n Markdown export: {md_path}")
