import json
from mistralai import Mistral, LibraryOut, DocumentOut, SDKError, ChatCompletionResponse, DocumentTextContent, \
    ResponseFormats, ResponseFormat
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

def update_document_name(client: Mistral, document: DocumentOut, library: LibraryOut, new_name: str):
    updated_doc = client.beta.libraries.documents.update(
        library_id=library.id,
        document_id=document.id,
        name=new_name
    )
    return updated_doc

def export_conjectures_to_json(response: ChatCompletionResponse, document: DocumentOut):
    Path("json_articles").mkdir(parents=True, exist_ok=True)

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

def get_mistral_reponse(client: Mistral, model: str, text_content: DocumentTextContent):
    return client.chat.complete(
        temperature=0,
        top_p=1,
        model=model,
        messages=[
            {"role": "user", "content": f"""VVoici le contenu de mon document: {text_content.text}\n\nMa question est la suivante, existe t-il des conjectures formulées par le(s) auteur(s) dans ce document ? Si oui, cite-les intégralement (mot à mot). Contraintes de sortie (TRÈS IMPORTANT) : - Tu dois répondre uniquement avec un objet JSON valide (UTF-8), sans aucun autre texte, sans balises et sans commentaires.
                - Respecte exactement le schéma ci-dessous.
                - Dans "text", mets la citation exacte de la conjecture depuis l'article ; remplace chaque retour à la ligne par \\n ; échappe les guillemets comme \\".
                - Si aucune conjecture n'est trouvée, mets "contains_conjecture": "no" et "conjectures": [].
                
                Schéma attendu (exemple de structure, pas un contenu) :
                {{
                  "titre_article": "<représente le nom du fichier PDF>",
                  "contains_conjecture": "yes" | "no",
                  "conjectures": [
                    {{
                      "id": "conjecture1",
                      "page": <la page de la conjecture>,
                      "text": "<citation exacte avec \\n pour les sauts de ligne et les guillemets échappés>"
                    }},
                    {{
                      "id": "conjecture2",
                      "page": <la page de la conjecture>,
                      "text": "<...>"
                    }}
                  ]
                }}
                """
            }
        ]
    )

def get_mistral_reponse_strict(client: Mistral, model: str, text_content: DocumentTextContent):
    return client.chat.complete(
        model=model,
        temperature=0,          # déterministe
        top_p=1,
        random_seed=0,          # idem: runs réplicables
        response_format=ResponseFormat(type="json_object"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a scholarly extraction engine. "
                    "Your job is to extract ONLY verbatim text spans from the provided document that satisfy STRICT criteria. "
                    "You MUST NOT paraphrase or invent content. If nothing matches, you MUST return that nothing was found."
                )
            },
            {
                "role": "user",
                "content": f"""
                TASK — EXTRACTION DE CONJECTURES FORMULÉES PAR LES AUTEURS (STRICT, VERBATIM)
                
                Définition (à respecter à la lettre) :
                - « Conjecture formulée par les auteurs » = EITHER
                  (A) un bloc/énoncé explicitement intitulé « Conjecture … » DANS CE DOCUMENT et NON attribué à d'autres personnes ; OU
                  (B) une phrase explicite des auteurs du type « We conjecture … » / « We formulate the following conjecture … » dans CE DOCUMENT.
                - À EXCLURE absolument :
                  * Problems / Questions / Open problems / Theorems / Lemmas / Corollaries / Claims / Definitions.
                  * Toute conjecture attribuée à d’autres (p. ex. « Tuza’s conjecture », « due to Aharoni and Zerbib », « as conjectured by X », références comme « [AZ20] », etc.).
                  * Toute conjecture des auteurs qui est ensuite réfutée par EUX dans ce même document (p. ex. « we disprove/refute/show it is false/does not hold »).
                
                CONTRAINTE VERBATIM & POSITION :
                - Chaque conjecture doit être une citation MOT-À-MOT qui apparaît EXACTEMENT dans le texte fourni ci-dessous (pas de reformulation).
                - Donne aussi les offsets caractère 0-based (char_start, char_end) dans le texte fourni.
                - Si tu ne peux pas fournir une citation EXACTE + offsets cohérents, N’INCLUS PAS l’item.
                
                RÉSULTAT ATTENDU (JSON UNIQUEMENT, AUCUN TEXTE AVANT/APRÈS) :
                {{
                  "titre_article": string,                  // meilleure estimation depuis les premières lignes, ou "" si incertain
                  "contains_conjecture": "yes" | "no",
                  "conjectures": [
                    {{
                      "id": string,                         // p.ex. "conj-1"
                      "text": string,                       // citation VERBATIM telle qu'elle apparaît
                      "char_start": integer,                // index 0-based dans le texte ci-dessous
                      "char_end": integer,                  // fin exclusive
                      "page": null,                         // laisse null si tu ne sais pas
                      "authorship": "author",               // DOIT être "author" (aucune conjecture citée)
                      "refuted_in_paper": boolean,          // true si les auteurs réfutent cette conjecture plus loin dans CE document
                      "authorship_evidence": string,        // mini-citation verbatim montrant que c’est bien leur conjecture (ex: "We conjecture ...")
                      "refutation_evidence": string | null  // mini-citation verbatim si réfutée ; sinon null
                    }}
                  ]
                }}
                
                RÈGLES DE SORTIE :
                1) Si aucun item ne satisfait TOUTES les conditions, renvoie exactement :
                   {{
                     "titre_article": "",
                     "contains_conjecture": "no",
                     "conjectures": []
                   }}
                2) AUCUN autre texte en dehors de l’objet JSON.
                
                --- BEGIN DOCUMENT TEXT ---
                {text_content.text}
                --- END DOCUMENT TEXT ---
                """
            }
        ]
    )

def get_dossier_json(dossier: str):
    dossier_path = Path(dossier)

    json_paths = sorted(
        p for p in dossier_path.iterdir()
        if p.is_file() and p.suffix.lower() == ".json"
    )

    json_conjectures = [p.name for p in json_paths]

    return json_conjectures