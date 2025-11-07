from __future__ import annotations
import argparse

from utils.deepseek_extract_pdf_to_text import extract_pdf_to_text
from utils.codex_prompts import *
from arxiv_api import *
from utils.extract_document_with_mistral import *

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

    # todo : pour chaque fichier, intérroger codex en lui donnant le chemin du fichier dans le prompt
    # il faut que lorsqu'il termine, pouvoir le killer pour passer au fichier suivant
    # on peut se dire qu'il doit créer un fichier avec les conjectures, et dès lors que le fichier existe et que la dernière ligne est "finish"
    # alors on kill le processus

    for idx, file_name in enumerate(deepseek_files):
        print(file_name)
        print("Lecture du fichier...")
        prompt = get_prompt_find_conjecture(deepseek_folder, file_name)
        os.execvp("codex", ["codex", "--sandbox=danger-full-access", prompt])

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

    # avec une clé classique je fais 10 uploads max avec une clé pro aussi
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
            sleep(25) # il faut attendre quelques instants le temps que le fichier s'upload avant d'extraire le contenu
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
    # create_excel_file(excel_file, sheet_name1, sheet_name2)
    #
    # query = extract_arxiv_query_py(boolean_query_file)
    # download_arxiv_pdfs(query, excel_file=excel_file, sheet_name=sheet_name1)

    # todo : voir pour extraire le contenu des articles au lieu de les uploads pour contourner la limite d'upload.

    # 1- trier les pdf
    # 2- lancer l'extraction via mistral et mettre le contenu dans un fichier texte
    # 3- si on atteint la limite alors pendre le relais avec deepseek

    load_dotenv()

    # Id du document 2508.16992v1 : 3259c8a5-0dcd-4b29-9531-bbaad4a90e6a

    # extract_documents("downloads/arxiv")

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

    # todo : délaisser mistral pour la détection des conjectures, je tiens une bonne piste assez fiable avec codex
    # find_conjectures("extraction/")
    find_conjectures_with_codex("extraction/")

    # update_excel_with_conjectures("articles.xlsx", "Articles", "Conjectures", Path("json_articles"))

    # todo : prochaine étape, faire la réfutation des conjectures.