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

def find_conjectures(client: Mistral, model: str):
    libraries = get_libraries(client)

    if len(libraries) == 0:
        library = create_library(client, "Librairie documents pdf", "Cette librairie contient tous les documents en format PDF récupérée depuis différentes bases de données.")
    else:
        library = libraries[0]

    print("Nombre total de documents : " + str(len(get_documents(library, client))))
    print("\n")
    print("Affichage des documents : \n")
    for document in get_documents(library, client):
        print("id : " + document.id + " - name : " + document.name)

        print(f"###### Détection de conjectures dans le document {document.name} ######")

        if document.id == "44c93cf3-76f2-4fa4-8595-60792e971872":
            print("Extraction de l'article choisi...")
            text_content = client.beta.libraries.documents.text_content(
                library_id=library.id,
                document_id=document.id
            )

            print("Mistral utilise le prompt pour extraire les conjectures..")
            response = get_mistral_reponse(client, model, text_content)
            print("Affichage de la réponse de Mistral : ")
            print(response)
            # todo : décommenter la fonction et la tester à nouveau
            # export_conjectures_to_json(response, document)

def extract_documents(dossier_articles: str, client: Mistral):
    dossier = get_dossier_pdfs(dossier_articles)

    libraries = get_libraries(client)
    library = libraries[0]
    indiceMistral = 0
    indiceDeepSeek = 0

    try:
        for pdf in dossier:
            document = upload_document(f"{dossier_articles}/{pdf}", pdf, client, library)
            indiceMistral += 1
            print(document)
            sleep(4)
    except SDKError:
        print("Limite d'upload d'articles atteinte avec Mistral.. DeepSeek prend le relais.")

        for pdf in dossier:
            if indiceDeepSeek != indiceMistral:
                indiceDeepSeek += 1
            else:
                os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")
                extract_pdf_to_text(f"{dossier_articles}/{pdf}","tests")

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
    api_key = os.getenv("MISTRAIL_API_KEY2")
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)

    extract_documents("", client)

    # todo : délaisser mistral pour la détection des conjectures, je tiens une bonne piste assez fiable avec codex
    # find_conjectures("downloads/arxiv")

    # update_excel_with_conjectures("articles.xlsx", "Articles", "Conjectures", Path("json_articles"))

    # todo : prochaine étape, faire la réfutation des conjectures.