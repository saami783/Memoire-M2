import os
import io
import time
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
from tqdm import tqdm

import torch
from transformers import AutoModel, AutoTokenizer


########################################
# CONFIG PAR DÉFAUT
########################################

MODEL_NAME = "deepseek-ai/DeepSeek-OCR"
MODEL_REV  = "main"  # tu peux mettre un hash de commit HF pour figer la version

# Prompt DeepSeek-OCR. Tu peux aussi tester "Convert the document to markdown."
DEFAULT_PROMPT = "<image>\n<|grounding|>Convert the document to text."

# Qualité / Vitesse :
#   fast   = +rapide, bon pour articles arXiv propres, peu de crops
#   gundam = +lent, meilleur sur pages très denses/scannées/tableaux serrés
QUALITY_PRESETS = {
    "fast": {
        "dpi": 120,         # rendu PDF -> image (plus bas que 144 = plus rapide)
        "base_size": 640,   # vue globale
        "image_size": 640,  # taille tuile locale (identique => pas de multi-tiles)
        "crop_mode": False, # pas de découpe multi-crops -> gros gain de vitesse
    },
    "gundam": {
        "dpi": 144,
        "base_size": 1024,
        "image_size": 640,
        "crop_mode": True,  # multi-crops haute résolution
    },
}

# Implémentation d'attention adaptée à Windows / RTX 20xx
ATTN_IMPL = "eager"

# Types de sorties que le modèle peut éventuellement écrire tout seul
READ_BACK_EXTS = (".md", ".mmd", ".txt")

# Ordre des dtypes essayés pour limiter la VRAM
DTYPE_TRY = ("bfloat16", "float16")


########################################
# CHARGEMENT MODELE / TOKENIZER
########################################

def _load_tokenizer():
    tok = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        revision=MODEL_REV,
    )

    # Patch pour calmer les warnings pad_token_id / attention_mask
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token

    return tok


def _load_model():
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        revision=MODEL_REV,
        use_safetensors=True,
        attn_implementation=ATTN_IMPL,
    ).eval()

    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA non disponible. DeepSeek-OCR est trop lourd pour CPU seul."
        )

    # Envoi sur GPU
    model = model.cuda()

    # On tente bfloat16 puis float16 pour réduire la VRAM et accélérer
    for dt in DTYPE_TRY:
        try:
            model = model.to(getattr(torch, dt))
            break
        except Exception:
            continue

    return model


########################################
# RENDU PDF -> IMAGES
########################################

def _pdf_to_images(pdf_path: Path, dpi: int):
    """
    Rend chaque page du PDF en image PIL RGB.
    On renvoie une liste d'images PIL en mémoire.
    """
    Image.MAX_IMAGE_PIXELS = None
    doc = fitz.open(str(pdf_path))

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    pages = []
    for p in doc:
        pix = p.get_pixmap(matrix=mat, alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        if img.mode != "RGB":
            img = img.convert("RGB")
        pages.append(img)

    doc.close()
    return pages


########################################
# RÉCUP FALLBACK SI infer() ÉCRIT SUR DISQUE
########################################

def _get_last_written_text_file(folder: Path, since_ts: float):
    """
    Certaines versions de model.infer() n'ont pas toujours un retour Python direct.
    Elles écrivent un .md/.txt dans output_path. On chope le dernier fichier écrit.
    """
    newest_path = None
    newest_mtime = since_ts

    for ext in READ_BACK_EXTS:
        for candidate in folder.glob(f"*{ext}"):
            try:
                mtime = candidate.stat().st_mtime
                if mtime >= newest_mtime:
                    newest_path = candidate
                    newest_mtime = mtime
            except FileNotFoundError:
                pass

    if newest_path is None:
        return ""

    try:
        return newest_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return newest_path.read_text(encoding="utf-8", errors="ignore")


########################################
# OCR D'UNE LISTE D'IMAGES (PIL)
########################################

@torch.no_grad()
def _ocr_pages_with_deepseek(
    pages,
    out_dir: Path,
    tok,
    model,
    prompt: str,
    base_size: int,
    image_size: int,
    crop_mode: bool,
):
    """
    Pour chaque image PIL :
    - sauvegarde temporaire en .jpg
    - appelle model.infer(...)
    - récupère le texte
    - renvoie une liste de strings (une par page)
    """

    tmp_dir = out_dir / "_tmp_pages"
    tmp_dir.mkdir(exist_ok=True)

    md_parts = []

    # autocast = exécuter en demi-précision => plus rapide / moins gourmand
    autocast_dtype = torch.bfloat16 if model.dtype == torch.bfloat16 else torch.float16

    for i, pil_img in enumerate(tqdm(pages, desc="OCR pages", unit="page")):
        # Sauvegarde rapide sur disque parce que infer() veut un chemin fichier
        page_path = tmp_dir / f"page_{i:04d}.jpg"
        # qualité 85 = plus petit que 92 donc I/O plus rapide, assez bon pour du texte propre
        pil_img.save(page_path, format="JPEG", quality=85)

        t0 = time.time()

        # On appelle le modèle en FP16/BF16
        with torch.autocast(device_type="cuda", dtype=autocast_dtype):
            res = model.infer(
                tok,
                prompt=prompt,
                image_file=str(page_path),
                output_path=str(out_dir),
                base_size=base_size,
                image_size=image_size,
                crop_mode=crop_mode,
                save_results=True,    # important : sinon parfois res=None
                test_compress=True,   # utilise la compression vision tokens DeepSeek
                # pas de do_sample / temperature ici -> ta version de infer() ne les accepte pas
            )

        # Essaye de lire le texte directement
        text = ""
        if isinstance(res, dict):
            text = res.get("text") or res.get("output") or ""

        # Sinon, fallback : aller lire le dernier .md/.txt généré juste après t0
        if not text.strip():
            text = _get_last_written_text_file(out_dir, since_ts=t0 - 0.5)

        # Nettoyage léger
        text = (
            text.replace("<｜end▁of▁sentence｜>", "")
                .replace("\u3000", " ")  # espace pleine largeur asiatique
                .strip()
        )

        md_parts.append(text)

    return md_parts


########################################
# FONCTION PUBLIQUE : CELLE QUE TU APPELLES
########################################

def extract_pdf_to_text(
    pdf_path: str,
    out_dir: str,
    *,
    prompt: str = DEFAULT_PROMPT,
    quality_mode: str = "fast",
):
    """
    C'est TA fonction publique.

    Exemple d'appel :
    extract_pdf_to_text(
        "downloads/arxiv/2508.16992v1.Online_Learning_for_Approximately_Convex_Functions_with_Long_term_Adversarial_Constraints.pdf",
        "extractions"
    )

    Arguments :
    - pdf_path (str)      : chemin du PDF
    - out_dir (str)       : dossier où écrire le résultat final .md et les fichiers temporaires
    - prompt (str)        : prompt passé à DeepSeek-OCR
    - quality_mode (str)  : "fast" ou "gundam"
        -> "fast"   = rapide, bon pour PDF propres (arXiv)
        -> "gundam" = lent mais plus robuste (rapports financiers scannés, journaux denses)
    """

    # 1. Prépare chemins
    pdf_path = Path(pdf_path).expanduser().resolve()
    out_dir = Path(out_dir).expanduser().resolve()

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "images").mkdir(exist_ok=True)

    # 2. Récupère les presets vitesse/qualité
    if quality_mode not in QUALITY_PRESETS:
        raise ValueError(f"quality_mode doit être dans {list(QUALITY_PRESETS.keys())}")
    preset = QUALITY_PRESETS[quality_mode]

    dpi        = preset["dpi"]
    base_size  = preset["base_size"]
    image_size = preset["image_size"]
    crop_mode  = preset["crop_mode"]

    print("[1/4] Chargement du tokenizer / modèle DeepSeek-OCR...")
    tok = _load_tokenizer()
    model = _load_model()

    print(f"[2/4] Rendu PDF -> images (dpi={dpi})...")
    pages = _pdf_to_images(pdf_path, dpi=dpi)

    print(f"[3/4] OCR DeepSeek-OCR ({quality_mode}) sur {len(pages)} page(s)...")
    md_pages = _ocr_pages_with_deepseek(
        pages=pages,
        out_dir=out_dir,
        tok=tok,
        model=model,
        prompt=prompt,
        base_size=base_size,
        image_size=image_size,
        crop_mode=crop_mode,
    )

    print("[4/4] Écriture du .md final...")
    combined_md = []
    for idx, page_text in enumerate(md_pages):
        combined_md.append(page_text)
        combined_md.append("\n\n<--- Page Split ({}) --->\n\n".format(idx))

    final_md_path = out_dir / (pdf_path.stem + ".md")
    final_md_path.write_text("".join(combined_md), encoding="utf-8")

    print("✅ Terminé.")
    print(f"   Résultat OCR : {final_md_path}")
    print("   (Chaque page est séparée par '<--- Page Split (page_index) --->')")


