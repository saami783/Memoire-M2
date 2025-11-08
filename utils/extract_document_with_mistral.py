from mistralai import Mistral, LibraryOut, DocumentOut, SDKError, DocumentTextContent
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

def upload_document(file_path: str, file_name: str, client: Mistral, library: LibraryOut):
    full_path = Path(file_path) / file_name if file_name else Path(file_path)
    with open(full_path, "rb") as file_content:
        uploaded_doc = client.beta.libraries.documents.upload(
            library_id=library.id,
            file=File(file_name=file_name, content=file_content),
        )
    return uploaded_doc

def update_document_name(client: Mistral, document: DocumentOut, library: LibraryOut, new_name: str):
    updated_doc = client.beta.libraries.documents.update(
        library_id=library.id,
        document_id=document.id,
        name=new_name
    )
    return updated_doc