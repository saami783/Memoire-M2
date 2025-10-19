import ast
import re

import arxiv
from pathlib import Path
import sys
from time import sleep
from tqdm import tqdm

OUTPUT_DIR = Path("downloads/arxiv")
BASE_PAGE_SIZE = 25
DELAY_SECONDS = 2
NUM_RETRIES = 3
LIMIT = None
SLEEP_ON_FAIL = 3
SOURCE = "arXiv"

def extract_arxiv_query_py(path: str) -> str:
    pattern = re.compile(
        r'^ARXIV_QUERY_PY:\s*query\s*=\s*(?P<lit>"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')\s*$',
        re.M
    )
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = pattern.search(text)
    if not m:
        raise ValueError("Ligne ARXIV_QUERY_PY introuvable dans le fichier.")
    return ast.literal_eval(m.group("lit"))

def _safe_first_author(result: arxiv.Result) -> str:
    try:
        return result.authors[0].name if result.authors else ""
    except Exception:
        return ""

def _safe_doi(result: arxiv.Result) -> str:
    return getattr(result, "doi", "") or ""

def _safe_published_iso(result: arxiv.Result) -> str:
    try:
        return result.published.isoformat()
    except Exception:
        return ""

def _article_row_with_id(next_id: int, result: arxiv.Result, file_name: str):
    # Id, Titre, Auteur, DOI, Date, Source, Lien, Fichier
    return [
        next_id,
        result.title,
        _safe_first_author(result),
        _safe_doi(result),
        _safe_published_iso(result),
        SOURCE,
        result.entry_id,
        file_name,
    ]

def _make_client(page_size: int) -> arxiv.Client:
    return arxiv.Client(
        page_size=page_size,
        delay_seconds=DELAY_SECONDS,
        num_retries=NUM_RETRIES,
    )

def download_arxiv_pdfs(query: str, excel_file: str = "articles.xlsx", sheet_name: str = "Feuille 1"):
    from utils.excel_service import open_or_create_excel, get_next_excel_id

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    wb = open_or_create_excel(excel_file, sheet_name)
    ws = wb[sheet_name]
    next_id = get_next_excel_id(ws)

    search = arxiv.Search(
        query=query,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    client = _make_client(BASE_PAGE_SIZE)

    total_seen = downloaded = skipped_exists = failed = appended = 0

    for result in tqdm(client.results(search), desc="Téléchargement des PDF"):
        total_seen += 1

        # print(result.title)
        # print(result.entry_id)
        # print(result.published)
        # print([a.name for a in result.authors])
        # print("PDF:", result.pdf_url)

        # Je skip si l'article est déjà présent (on détecte par préfixe ID court)
        short_id = result.get_short_id().replace("/", "_")
        existing = sorted(OUTPUT_DIR.glob(f"{short_id}*.pdf"))
        if existing:
            skipped_exists += 1
            continue

        success = False
        for attempt in range(1, NUM_RETRIES + 1):
            try:
                before = set(OUTPUT_DIR.iterdir())
                saved_path = result.download_pdf(dirpath=str(OUTPUT_DIR))

                # Certaines versions renvoient le chemin : on le prend si dispo
                if saved_path:
                    from pathlib import Path
                    saved = Path(saved_path)
                else:
                    # Fallback diff avant/après pour détecter les nouveaux fichiers
                    after = set(OUTPUT_DIR.iterdir())
                    new_files = [p for p in (after - before) if p.suffix.lower() == ".pdf"]
                    if not new_files:
                        raise RuntimeError("Aucun fichier PDF détecté après téléchargement")
                    saved = max(new_files, key=lambda p: p.stat().st_mtime)

                downloaded += 1
                ws.append(_article_row_with_id(next_id, result, saved.name))
                next_id += 1
                appended += 1

                if downloaded % 20 == 0:
                    wb.save(excel_file)

                success = True
                break
            except Exception as e:
                if attempt < NUM_RETRIES:
                    sleep(SLEEP_ON_FAIL)
                else:
                    failed += 1
                    print(f"[ERREUR] {result.get_short_id()} : {e}", file=sys.stderr)

    wb.save(excel_file)
    print(
        f"\nTerminé.\n"
        f"- Nouveaux téléchargements : {downloaded}\n"
        f"- PDF déjà présents        : {skipped_exists}\n"
        f"- Échecs                   : {failed}\n"
        f"- Lignes ajoutées Excel    : {appended}\n"
        f"- Total parcouru           : {total_seen}"
    )
