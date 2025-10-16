import os
from mistralai import Mistral, LibraryOut, DocumentOut
from dotenv import load_dotenv
from mistralai.models import File

def send_prompt(prompt: str, model: str, client: Mistral):
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )
    print(chat_response.choices[0].message.content)

def get_models(client: Mistral):
    models = client.models.list().data
    for model in models:
        print(model.name)

def create_library(client: Mistral, library_name: str, library_description: str):
    new_library = client.beta.libraries.create(name=library_name, description=library_description)
    return new_library

def get_libraries(client: Mistral):
    libraries = client.beta.libraries.list().data

    for library in libraries:
        print(library.name, f"with {library.nb_documents} documents.")
    return libraries

def get_library(library: LibraryOut, client: Mistral):
    library = client.beta.libraries.get(library_id=library.id)
    print(library.name, f"with {library.nb_documents} documents.")
    return library

def get_document(library: LibraryOut, client: Mistral):
    doc_list = client.beta.libraries.documents.list(library_id=library.id).data
    for doc in doc_list:
        print(f"{doc.name}: {doc.extension} with {doc.number_of_pages} pages.")
        print(f"{doc.summary}")


def delete_library(new_library: LibraryOut, client: Mistral):
    client.beta.libraries.delete(library_id=new_library.id)

def delete_document(new_library: LibraryOut, document: DocumentOut, client: Mistral):
    client.beta.libraries.documents.delete(library_id=new_library.id, document_id=document.id)

def upload_file(file_path: str, client: Mistral, new_library: LibraryOut):
    with open(file_path, "rb") as file_content:
        uploaded_doc = client.beta.libraries.documents.upload(
            library_id=new_library.id,
            file=File(fileName="mistral7b.pdf", content=file_content),
        )

def create_library_agent(new_library):
    library_agent = client.beta.agents.create(
        model="mistral-medium-2505",
        name="Document Library Agent",
        description="Agent used to access documents from the document library.",
        instructions="Use the  library tool to access external documents.",
        tools=[{"type": "document_library", "library_ids": [new_library.id]}],
        completion_args={
            "temperature": 0.3,
            "top_p": 0.95,
        }
    )
    return library_agent

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("MISTRAIL_API_KEY")

    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    library = create_library(client, "test_library", "Ma description")

    get_libraries(client)