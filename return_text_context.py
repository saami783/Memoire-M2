from dotenv import load_dotenv
import os
from time import sleep
from find_conjectures_mistral import *
import sys

def extract_document(library: LibraryOut, document: DocumentOut, client: Mistral):

    return client.beta.libraries.documents.text_content(
        library_id=library.id,
        document_id=document.id
    )

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("MISTRAIL_API_KEY2")
    client = Mistral(api_key=api_key)

    article = sys.argv[1] if len(sys.argv) > 1 else "inconnu"

    dossier_articles = "downloads/arxiv"

    dossier = get_dossier_pdfs(dossier_articles)

    libraries = get_libraries(client)

    library = libraries[0]

    try:
        document = upload_document(f"{dossier_articles}/", f"{article}.pdf", client, library)
        print(document)
        sleep(2)
        text_content = extract_document(library, document, client)
        delete_document(library, document, client)
    except SDKError:
        print("Limite d'upload d'articles atteinte.")
