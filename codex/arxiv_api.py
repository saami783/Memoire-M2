import arxiv
from pathlib import Path
import sys
from time import sleep
from tqdm import tqdm
import re
import ast
from utils.excel_service import open_excel_file

OUTPUT_DIR = Path("pdf_arxiv_vertex_cover")
PAGE_SIZE = 100
DELAY_SECONDS = 1
NUM_RETRIES = 3
LIMIT = None
SLEEP_ON_FAIL = 3

def safe_name(s: str, max_len: int = 140) -> str:
    """Nettoie pour créer un nom de fichier sûr."""
    s = re.sub(r"[\\/:*?\"<>|]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:max_len].rstrip()

def pdf_path(out_dir: Path, r: arxiv.Result) -> Path:
    return out_dir / f"{r.get_short_id()} - {safe_name(r.title)}.pdf"

def download_arxiv_pdfs(query: str):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    search = arxiv.Search(
        query=query,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    client = arxiv.Client(
        page_size=PAGE_SIZE,
        delay_seconds=DELAY_SECONDS,
        num_retries=NUM_RETRIES,
    )

    total_seen = 0
    downloaded = 0
    skipped = 0
    failed = 0

    iterator = client.results(search)
    if LIMIT is not None:
        iterator = (r for i, r in enumerate(iterator, 1) if i <= LIMIT)

    for r in tqdm(iterator, desc="Téléchargement des PDF"):
        total_seen += 1
        target = pdf_path(OUTPUT_DIR, r)

        # Skip si déjà présent
        if target.exists() and target.stat().st_size > 0:
            skipped += 1
            continue

        # Tenter quelques fois (en plus des retries réseau du client)
        for attempt in range(1, 1 + NUM_RETRIES):
            try:
                r.download_pdf(dirpath=OUTPUT_DIR, filename=target.name)
                downloaded += 1
                break
            except Exception as e:
                if attempt < NUM_RETRIES:
                    sleep(SLEEP_ON_FAIL)
                else:
                    failed += 1
                    print(f"[ERREUR] {r.get_short_id()} : {e}", file=sys.stderr)

    print(
        f"\nTerminé.\n"
        f"- Nouveaux téléchargements : {downloaded}\n"
        f"- Déjà présents            : {skipped}\n"
        f"- Échecs                   : {failed}\n"
        f"- Total parcouru           : {total_seen}"
    )

def extract_arxiv_query_py(path: str) -> str:
    """
    Retourne la requête (string) définie dans la ligne:
      ARXIV_QUERY_PY: query = "<...>"
    du fichier `path`.

    Lève ValueError si la ligne est introuvable.
    """
    pattern = re.compile(
        r'^ARXIV_QUERY_PY:\s*query\s*=\s*(?P<lit>"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')\s*$',
        re.M
    )
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = pattern.search(text)
    if not m:
        raise ValueError("Ligne ARXIV_QUERY_PY introuvable dans le fichier.")
    # Convertit le littéral Python en vraie chaîne (déséchappe les \" etc.)
    return ast.literal_eval(m.group("lit"))

def write_artiles_into_excel(excel_file: str):
    wb = open_excel_file(excel_file)