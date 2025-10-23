from __future__ import annotations
import argparse
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

def find_conjectures(dossier_articles: str):
    load_dotenv()
    # api_key = os.getenv("MISTRAIL_API_KEY")
    api_key = os.getenv("MISTRAIL_API_KEY2")

    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    libraries = get_libraries(client)

    if len(libraries) == 0:
        library = create_library(client, "Librairie documents pdf", "Cette librairie contient tous les documents en format PDF récupérée depuis différentes bases de données.")
    else:
        library = libraries[0]

    dossier = get_dossier_pdfs(dossier_articles)

    try:
        for pdf in dossier:
            # document = upload_document(f"{dossier_articles}/{pdf}", pdf, client, library)
            # print(document)
            sleep(4)
    except SDKError:
        print("Limite d'upload d'articles atteinte.")

    document = get_document(library, "25079da6-7fc3-4262-963b-e500b754e930", client)
    # for document in get_documents(library, client):

    print(f"###### Détection de conjectures dans le document {document.name} ######")

    text_content = client.beta.libraries.documents.text_content(
        library_id=library.id,
        document_id=document.id
    )

    response = get_mistral_reponse(client, model, text_content)
    print(response)
    export_conjectures_to_json(response, document)


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
    # # @todo Prendre en charges d'autres bases de données (implique de modifier le prompt aussi)
    #
    # excel_file = "articles.xlsx"
    # sheet_name1 = "Articles"
    # sheet_name2 = "Conjectures"
    # create_excel_file(excel_file, sheet_name1, sheet_name2)
    #
    # query = extract_arxiv_query_py(boolean_query_file)
    # download_arxiv_pdfs(query, excel_file=excel_file, sheet_name=sheet_name1)

    print("Process completed.")

    # todo : voir pour extraire le contenu des articles au lieu de les uploads pour contourner la limite d'upload.
    # find_conjectures("downloads/arxiv")
    find_conjectures("test")

    update_excel_with_conjectures("articles.xlsx", "Articles", "Conjectures", Path("json_articles"))

    # todo : prochaine étape, faire la réfutation des conjectures.