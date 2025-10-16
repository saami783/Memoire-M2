import arxiv
from pathlib import Path
import sys
from time import sleep
from tqdm import tqdm
import re
import ast
from utils.excel_service import open_or_create_excel, get_next_excel_id

OUTPUT_DIR = Path("pdf_arxiv_vertex_cover")
BASE_PAGE_SIZE = 25
DELAY_SECONDS = 2
NUM_RETRIES = 3
LIMIT = None
SLEEP_ON_FAIL = 3
SOURCE = "arXiv"

def safe_name(s: str, max_len: int = 140) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:max_len].rstrip()

def pdf_path(out_dir: Path, r: arxiv.Result) -> Path:
    return out_dir / f"{r.get_short_id()} - {safe_name(r.title)}.pdf"

def _authors_str(r: arxiv.Result) -> str:
    try:
        return ", ".join(a.name for a in r.authors)
    except Exception:
        return ""

def _doi_str(r: arxiv.Result) -> str:
    return getattr(r, "doi", None) or ""

def _pub_date_str(r: arxiv.Result) -> str:
    try:
        return r.published.date().isoformat()
    except Exception:
        return ""

def _article_row_with_id(next_id: int, r: arxiv.Result):
    # Id, Titre, Auteur, DOI, Date, Source, Lien, Conjecture
    return [
        next_id,
        r.title,
        _authors_str(r),
        _doi_str(r),
        _pub_date_str(r),
        SOURCE,
        r.entry_id,
        "",
    ]

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

def _make_client(page_size: int) -> arxiv.Client:
    return arxiv.Client(
        page_size=page_size,
        delay_seconds=DELAY_SECONDS,
        num_retries=NUM_RETRIES,
    )

def _resilient_results(search: arxiv.Search, start_index: int = 0):
    """
    Générateur résilient: reprend après une page vide / erreur transitoire.
    - saute `already_yielded` premiers résultats à chaque reprise
    - backoff exponentiel en cas d’échec
    """
    already_yielded = start_index
    page_size = BASE_PAGE_SIZE
    backoff = 2

    while True:
        client = _make_client(page_size)
        try:
            i = 0
            for r in client.results(search):
                if i < already_yielded:
                    i += 1
                    continue
                yield r
                already_yielded += 1
                i += 1
            # si on sort proprement de la boucle, c’est fini
            return
        except arxiv.UnexpectedEmptyPageError as e:
            # page vide → attendre et réessayer avec backoff
            print(f"[WARN] Page vide détectée, reprise après {already_yielded} items. Backoff {backoff}s.", file=sys.stderr)
            sleep(backoff)
            # réduire encore la page pour stabiliser
            page_size = max(10, page_size // 2) if page_size > 10 else page_size
            backoff = min(backoff * 2, 30)
            continue
        except Exception as e:
            print(f"[WARN] Erreur transitoire ({type(e).__name__}): {e}. Reprise après {already_yielded} items dans {backoff}s.", file=sys.stderr)
            sleep(backoff)
            backoff = min(backoff * 2, 30)
            continue

def download_arxiv_pdfs(query: str, excel_file: str = "articles.xlsx", sheet_name: str = "Feuille 1"):
    """
    Télécharge les PDFs. Écrit dans Excel uniquement si le téléchargement a réussi.
    - Append à la ligne n+1 avec un ID interne auto-incrémenté.
    - Aucun dédoublonnage.
    - Résilient à UnexpectedEmptyPageError (reprise où on s’est arrêté).
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    wb = open_or_create_excel(excel_file, sheet_name)
    ws = wb[sheet_name]
    next_id = get_next_excel_id(ws)

    search = arxiv.Search(
        query=query,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    total_seen = 0
    downloaded = 0
    skipped_exists = 0
    failed = 0
    appended = 0

    iterator = _resilient_results(search)
    if LIMIT is not None:
        iterator = (r for i, r in enumerate(iterator, 1) if i <= LIMIT)

    for r in tqdm(iterator, desc="Téléchargement des PDF"):
        total_seen += 1
        target = pdf_path(OUTPUT_DIR, r)

        if target.exists() and target.stat().st_size > 0:
            skipped_exists += 1
            continue

        # Télécharger avec quelques tentatives locales
        success = False
        for attempt in range(1, 1 + NUM_RETRIES):
            try:
                r.download_pdf(dirpath=OUTPUT_DIR, filename=target.name)
                success = True
                break
            except Exception as e:
                if attempt < NUM_RETRIES:
                    sleep(SLEEP_ON_FAIL)
                else:
                    failed += 1
                    print(f"[ERREUR] {r.get_short_id()} : {e}", file=sys.stderr)

        if success:
            downloaded += 1
            ws.append(_article_row_with_id(next_id, r))
            next_id += 1
            appended += 1

            if downloaded % 20 == 0:
                wb.save(excel_file)

    wb.save(excel_file)
    print(
        f"\nTerminé.\n"
        f"- Nouveaux téléchargements : {downloaded}\n"
        f"- PDF déjà présents        : {skipped_exists}\n"
        f"- Échecs                   : {failed}\n"
        f"- Lignes ajoutées Excel    : {appended}\n"
        f"- Total parcouru           : {total_seen}"
    )
