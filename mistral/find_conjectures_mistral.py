import json
import os
from time import sleep
from dotenv import load_dotenv
from mistralai import Mistral, LibraryOut, DocumentOut, SDKError, ChatCompletionResponse
from mistralai.models import File
from pathlib import Path

def get_models(client: Mistral):
    models = client.models.list().data
    for model in models:
        print(model.name)

def create_library(client: Mistral, library_name: str, library_description: str):
    new_library = client.beta.libraries.create(name=library_name, description=library_description)
    return new_library

def get_libraries(client: Mistral):
    libraries = client.beta.libraries.list().data
    return libraries

def get_library(library_id, client: Mistral):
    library = client.beta.libraries.get(library_id=library_id)
    return library

def get_documents(library: LibraryOut, client: Mistral):
    doc_list = client.beta.libraries.documents.list(library_id=library.id).data
    return doc_list

def get_document(library: LibraryOut, document_id: str, client: Mistral):
    doc = client.beta.libraries.documents.get(library_id=library.id, document_id=document_id)
    return doc

def delete_library(library: LibraryOut, client: Mistral):
    client.beta.libraries.delete(library_id=library.id)

def delete_document(library: LibraryOut, document: DocumentOut, client: Mistral):
    client.beta.libraries.documents.delete(library_id=library.id, document_id=document.id)

def upload_document(file_path: str, client: Mistral, library: LibraryOut):
    with open(file_path, "rb") as file_content:
        uploaded_doc = client.beta.libraries.documents.upload(
            library_id=library.id,
            file=File(file_name=file_path, content=file_content),
        )
    return uploaded_doc

def create_library_agent(new_library, client):
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

def get_dossier_pdfs(dossier: str):
    dossier_path = Path(dossier)

    pdf_paths = sorted(
        p for p in dossier_path.iterdir()
        if p.is_file() and p.suffix.lower() == ".pdf"
    )

    noms_pdfs = [p.name for p in pdf_paths]

    return noms_pdfs

def export_conjectures_to_json(response: ChatCompletionResponse, document: DocumentOut):
    try:
        lines = (response.choices[0].message.content or "").splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)

        data = json.loads(raw)

        out_path = Path(f"json_articles/{document.name}.json")
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Fichier écrit : {out_path.resolve()}")

        # delete_document(library, document, client)

    except json.JSONDecodeError as e:
        print("La réponse n'est pas un JSON valide :", e)