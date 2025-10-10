from __future__ import annotations
import argparse
from utils.create_pico_file import create_pico_file
from utils.codex_prompts import *
from utils.create_boolean_queries_file import create_boolean_queries_file
import arxiv
from arxiv_api import *
from utils.excel_service import *
from utils.find_conjectures import *

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère un PICO via Codex puis continue (Unix/macOS).")
    p.add_argument("question", nargs="?", help="Question de recherche.")
    return p.parse_args()

def main() -> str | None:
    args = parse_args()
    if not args.question:
        print("No research question provided.", file=sys.stderr)
        return None
    print(args.question)
    return args.question

if __name__ == "__main__":
    research_question = main()
    boolean_query_file = "boolean_queries.txt"
    pico_prompt = get_prompt_to_generate_pico(research_question, "PICO{research_question}.txt")

    create_pico_file(pico_prompt)

    pico_filename = f"PICO_{research_question}.txt"

    boolean_query_prompt = get_prompt_to_generate_boolean_query(
        pico_filename=pico_filename,
        research_question=research_question,
        output_file_name_boolean_queries="boolean_queries",
        doc_boolean_queries="doc_boolean_queries",
    )

    create_boolean_queries_file(boolean_query_prompt, filename=boolean_query_file)

    # @todo Prendre en charges d'autres bases de données (implique de modifier le prompt aussi)

    excel_file = "articles.xlsx"
    sheet_name1 = "Articles"
    sheet_name2 = "Conjectures"
    create_excel_file(excel_file, sheet_name1, sheet_name2)

    query = extract_arxiv_query_py(boolean_query_file)
    download_arxiv_pdfs(query, excel_file=excel_file, sheet_name=sheet_name1)

    find_conjecture_prompt = get_prompt_to_find_conjectures_in_pdfs("", "articles.xlsx")
    sentinel = run_conjecture_analysis(find_conjecture_prompt)

    print("Process completed.")