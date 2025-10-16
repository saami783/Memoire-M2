import os
from mistralai import Mistral
from dotenv import load_dotenv

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

def create_library(client: Mistral):
    new_library = client.beta.libraries.create(name="Test lib", description="A simple library with information about Mistral models.")
    return new_library

def get_library(client: Mistral):
    libraries = client.beta.libraries.list().data

    for library in libraries:
        print(library.name, f"with {library.nb_documents} documents.")

def get_document(libraries, client: Mistral):
    if len(libraries) == 0:
        print("No libraries found.")
    else:
        doc_list = client.beta.libraries.documents.list(library_id=libraries[0].id).data
        for doc in doc_list:
            print(f"{doc.name}: {doc.extension} with {doc.number_of_pages} pages.")
            print(f"{doc.summary}")


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("MISTRAIL_API_KEY")

    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    get_library(client)