from __future__ import annotations
import argparse
from utils.create_pico_file import create_pico_file
from utils.codex_prompts import *
from utils.create_boolean_queries_file import create_boolean_queries_file
from arxiv_api import *
from utils.excel_service import *
from find_conjectures_mistral import *

import ssl, certifi
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
    load_dotenv()
    api_key = os.getenv("MISTRAIL_API_KEY")
    # api_key2 = os.getenv("MISTRAIL_API_KEY2")

    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    libraries = get_libraries(client)
    library = libraries[0]

    if len(libraries) == 0:
        library = create_library(client, "Librairie documents pdf", "Cette librairie contient tous les documents en format PDF récupérée depuis différentes bases de données.")

    dossier = get_dossier_pdfs('pdf_arxiv_vertex_cover')

    try:
        for pdf in dossier:
            print(pdf)
            upload_document(f"pdf_arxiv_vertex_cover/{pdf}", pdf, client, library)
            sleep(4)
    except SDKError:
        print("Limite d'upload d'articles atteinte.")

    for document in get_documents(library, client):

        print(f"###### Détection de conjectures dans le document {document.name} ######")

        text_content = client.beta.libraries.documents.text_content(
            library_id=library.id,
            document_id=document.id
        )

        response = get_mistral_reponse(client, model, text_content)
        export_conjectures_to_json(response, document)


if __name__ == "__main__":
    research_question = get_research_question_arg()
    boolean_query_file = "boolean_queries.txt"
    pico_prompt = get_prompt_to_generate_pico(research_question, f"PICO{research_question}.txt")

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

    # print("Process completed.")
    #
    # find_conjectures()
    #
    # # todo : extraire les informations des conjectures json dans un fichier excel.
    #
    # print(get_dossier_json("json_articles"))
    #
    # # todo : prochaine étape, faire la réfutation des conjectures.