from __future__ import annotations
import argparse

from utils.codex_create_boolean_queries_file import create_boolean_queries_file
from utils.codex_create_json_conjecture import create_json_conjecture
from utils.codex_create_pico_file import create_pico_file
from utils.deepseek_extract_pdf_to_text import extract_pdf_to_text
from utils.codex_prompts import *
from arxiv_api import *
from utils.excel_service import create_excel_file
from utils.extract_document_with_mistral import *
from utils.test import update_excel_with_conjectures

import os
from time import sleep
from dotenv import load_dotenv
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Génère un PICO via Codex puis continue (Unix/macOS).")
    p.add_argument("question", nargs="?", help="Question de recherche.")
    return p.parse_args()

def get_research_question_arg() -> str | None:
    args = parse_args()
    if not args.question:
        print("No research question provided.", file=sys.stderr)
        return None
    print(args.question)
    return args.question

def find_conjectures_with_codex(dossier_articles: str):
    mistral_folder = dossier_articles+"mistral"
    deepseek_folder = dossier_articles+"deepseek"

    mistral_files = get_dossier_with_files(mistral_folder, ".txt")

    deepseek_files = get_dossier_with_files(deepseek_folder, ".txt")

    for idx, file_name in enumerate(mistral_files):
        print(file_name)
        print("Lecture du fichier...")
        prompt = get_prompt_find_conjecture(mistral_folder, file_name)
        create_json_conjecture(
            prompt,
            Path(mistral_folder + "/json"),
            codex_cwd=Path("."),
        )

    # for idx, file_name in enumerate(mistral_files):
    #     print(file_name)
    #     print("Lecture du fichier...")
    #
    #     break

def extract_documents(dossier_articles: str):
    """
    Utilise Mistral pour upload des documents puis extraire le contenu.
    Si la limite d'utilisation est dépassée, on bascule sur deepseek-ocr.
    """
    pdfs = get_dossier_with_files(dossier_articles, ".pdf")

    api_key = os.getenv("MISTRAIL_API_KEY_PRO")
    client = Mistral(api_key=api_key)

    libraries = get_libraries(client)
    library = libraries[0]

    for idx, pdf in enumerate(pdfs):
        file_name = pdf

        try:
            print(f"Tentative d'upload du pdf {pdf}")
            document = upload_document(dossier_articles, file_name, client, library)
            print("Le document a bien été uploadé.")
            print(f"Id du document : {document.id}")
            sleep(30) # il faut attendre quelques instants le temps que le fichier s'upload avant d'extraire le contenu
            print("Tentative d'extraction du contenu du document...")
            text_content = client.beta.libraries.documents.text_content(
                library_id=library.id,
                document_id=document.id
            )
            print("Extraction avec succès.")
            print("Tentative de sauvegarde du contenu dans un fichier txt...")
            save_text_result(pdf, text_content.text, True)
            sleep(4)

        except SDKError:
            print("Exception SDKError levée.")

            # run_deepseek(pdf_path)
            #
            # for reste_pdf in pdfs[idx+1:]:
            #     reste_path = f"{dossier_articles}/{reste_pdf}"
            #     run_deepseek(reste_path)

                # test_pdf = r"downloads\arxiv\2508.16992v1.Online_Learning_for_Approximately_Convex_Functions_with_Long_term_Adversarial_Constraints.pdf"
                # test_out = r"extractions"
                # DEFAULT_PROMPT = "<image>\n<|grounding|>Convert the document to text."
                #
                # extract_pdf_to_text(
                #     pdf_path=test_pdf,
                #     out_dir=test_out,
                #     prompt=DEFAULT_PROMPT,
                #     quality_mode="fast",
                # )

    print("Tous les PDFs ont été traités par Mistral sans bascule DeepSeek.")

def get_dossier_with_files(dossier: str, extension: str):
    dossier_path = Path(dossier)

    fichier_paths = sorted(
        f for f in dossier_path.iterdir()
        if f.is_file() and f.suffix.lower() == extension
    )

    noms_fichiers = [f.name for f in fichier_paths]

    return noms_fichiers

def get_dossier_json(dossier: str):
    dossier_path = Path(dossier)

    json_paths = sorted(
        p for p in dossier_path.iterdir()
        if p.is_file() and p.suffix.lower() == ".json"
    )

    json_conjectures = [p.name for p in json_paths]

    return json_conjectures

def save_text_result(pdf_name: str, text_content: str, is_mistral: bool):
    parent_folder = "extraction"
    mistral_fodler = f"{parent_folder}/mistral"
    deepseek_folder = f"{parent_folder}/deepseek"

    os.makedirs(f"{parent_folder}", exist_ok=True)
    os.makedirs(f"{mistral_fodler}", exist_ok=True)
    os.makedirs(f"{deepseek_folder}", exist_ok=True)

    if is_mistral:
        out_path = f"{mistral_fodler}/{pdf_name}.txt"
    else:
        out_path = f"{deepseek_folder}/{pdf_name}.txt"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text_content)

    print("Le contenu du fichier a bien été sauvegardé.")

def run_deepseek(pdf_path: str):
    os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    extract_pdf_to_text(pdf_path, "extractions")

if __name__ == "__main__":
    # research_question = get_research_question_arg()
    # boolean_query_file = "boolean_queries.txt"
    # pico_prompt = get_prompt_to_generate_pico(research_question, f"PICO{research_question}.txt")
    #
    # create_pico_file(pico_prompt)
    #
    # pico_filename = f"PICO_{research_question}.txt"
    #
    # boolean_query_prompt = get_prompt_to_generate_boolean_query(
    #     pico_filename=pico_filename,
    #     research_question=research_question,
    #     output_file_name_boolean_queries="boolean_queries",
    #     doc_boolean_queries="doc_boolean_queries",
    # )
    #
    # create_boolean_queries_file(boolean_query_prompt, filename=boolean_query_file)
    #
    # excel_file = "articles.xlsx"
    # sheet_name1 = "Articles"
    # sheet_name2 = "Conjectures"
    # sheet_name3 = "Parametres"
    # create_excel_file(excel_file, sheet_name1, sheet_name2, sheet_name3)
    #
    # query = extract_arxiv_query_py(boolean_query_file)
    # download_arxiv_pdfs(query, excel_file=excel_file, sheet_name=sheet_name1)

    load_dotenv()

    # extract_documents("downloads/arxiv")

    # todo : éclaircir ce qu'on veut vraiment définir comme étant une conjecture. À l'heure actuelle codex n'a pas un comportement déterministe avec ça.
    # find_conjectures_with_codex("extraction/")

    # todo : mettre à jour le fichier excel avec les conjectures et les paramètres associés
    update_excel_with_conjectures()