from __future__ import annotations
import argparse

from deepseek_extract_pdf_to_text import extract_pdf_to_text
from utils.create_pico_file import create_pico_file
from utils.codex_prompts import *
from utils.create_boolean_queries_file import create_boolean_queries_file
from arxiv_api import *
from utils.excel_service import *
from find_conjectures_mistral import *
from utils.update_conjecture_excel import update_excel_with_conjectures

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

def find_conjectures():
    api_key = os.getenv("MISTRAIL_API_KEY_PRO")
    model = "mistral-large-latest" # le modèle est limité, il faut utiliser minimistral 8b
    client = Mistral(api_key=api_key)
    # tester si la performance change en fonction du fichier txt ou du document passé au prompt. => lorsqu'il n'y a pas de conjectures, les réponses sont iso
    # todo : tester avec une conjecture

    # tester avec le modèle de deepseek s'il sait reconnaître des conjectures

    libraries = get_libraries(client)
    library = libraries[0]

    document = get_document(library, "5ad2b09c-ef27-48a8-a438-2798bf1f622c", client)

    text_content = client.beta.libraries.documents.text_content(
        library_id=library.id,
        document_id=document.id
    )

    print("Mistral utilise le prompt pour extraire les conjectures..")
    response = get_mistral_reponse(client, model, text_content)
    print("Affichage de la réponse de Mistral via le document de la librairie: ")
    print(response)

    sleep(15)

    with open("extraction/mistral/2106.03594v3.Learning_Combinatorial_Node_Labeling_Algorithms.pdf.txt", "r", encoding="utf-8") as f:
        contenu = f.read()
    print("\n")
    response_from_txt = get_mistral_reponse_from_text(client, model, contenu)
    print("Affichage de la réponse de Mistral via le fichier texte : ")
    print(response_from_txt)


    # todo : décommenter la fonction et la tester à nouveau
    # export_conjectures_to_json(response, document)

def extract_documents(dossier_articles: str):
    """
    Utilise Mistral pour upload des documents puis extraire le contenu.
    Si la limite d'utilisation est dépassée, on bascule sur deepseek-ocr.
    """
    pdfs = get_dossier_pdfs(dossier_articles)

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
            sleep(10) # il faut attendre quelques instants le temps que le fichier s'upload avant d'extraire le contenu
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
    find_conjectures()

    # update_excel_with_conjectures("articles.xlsx", "Articles", "Conjectures", Path("json_articles"))

    # todo : prochaine étape, faire la réfutation des conjectures.