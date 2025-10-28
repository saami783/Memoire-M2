from dotenv import load_dotenv
import os
from time import sleep
from find_conjectures_mistral import *

load_dotenv()
api_key = os.getenv("MISTRAIL_API_KEY2")
# model = "mistral-large-latest"
model = "ministral-8b-2410"
client = Mistral(api_key=api_key)

def test_find_conjectures(iteration: int, document: DocumentOut, text_content: DocumentTextContent):

    print(f"Récupération de la réponse de de l'article {document.name}...")

    response = get_mistral_reponse(client, model, text_content)

    # print("Affichage de la réponse : \n")
    # print(response)
    # print("\n")

    try:
        content = response.choices[0].message.content
    except Exception:
        blocks = getattr(response.choices[0].message, "content", [])
        if isinstance(blocks, list):
            content = "".join(
                b.get("text", "") for b in blocks if
                isinstance(b, dict) and b.get("type") in (None, "output_text", "text")
            )
        else:
            content = str(response)

    os.makedirs("./conjectures", exist_ok=True)
    with open(f"./conjectures/conjectures_{iteration}.txt", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    libraries = get_libraries(client)

    if len(libraries) == 0:
        library = create_library(client, "Librairie documents pdf",
                   "Cette librairie contient tous les documents en format PDF récupérée depuis différentes bases de données.")
    else:
        library = libraries[0]

    document = get_document(library, "44c93cf3-76f2-4fa4-8595-60792e971872", client)

    text_content = client.beta.libraries.documents.text_content(
        library_id=library.id,
        document_id=document.id
    )

    for i in range(8):
        test_find_conjectures(i, document, text_content)
        sleep(5)