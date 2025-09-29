import requests
"""
-- Paramètres utiles :

q=... → ta requête (syntax style Lucene / Solr).

wt=json → sortie en JSON.

fl= → liste des champs à retourner (par défaut beaucoup trop).

rows= → nombre de résultats.

-- Champs de recherche principaux :

title_t → titre de la publication.

abstract_s → résumé.

authFullName_s → auteur.

keyword_s → mots-clés.

submittedDate_tdate → date de dépôt.

"""


# url = "https://api.archives-ouvertes.fr/search/"
# params = {
#     "q": "(title_t:graph AND title_t:learning) NOT title_t:quantum",
#     "fl": "title_s,authFullName_s,uri_s",
#     "rows": 5,
#     "wt": "json"
# }
#
# r = requests.get(url, params=params)
# data = r.json()
#
# for doc in data["response"]["docs"]:
#     print(doc["title_s"][0])
#     print("URL:", doc["uri_s"][0])
#     print("-" * 80)


import requests

def build_hal_query(title_terms=None, abstract_terms=None, keyword_terms=None, operator="OR"):
    """
    Construit une requête booléenne pour HAL à partir de listes de mots-clés.
    - title_terms : liste de mots-clés à chercher dans le titre
    - abstract_terms : liste de mots-clés à chercher dans l'abstract
    - keyword_terms : liste de mots-clés à chercher dans les mots-clés
    - operator : "OR" ou "AND" (pour combiner les termes à l’intérieur d’un champ)
    """
    query_parts = []

    if title_terms:
        title_query = f" {operator} ".join([f"title_t:\"{t}\"" for t in title_terms])
        query_parts.append(f"({title_query})")

    if abstract_terms:
        abs_query = f" {operator} ".join([f"abstract_s:\"{t}\"" for t in abstract_terms])
        query_parts.append(f"({abs_query})")

    if keyword_terms:
        kw_query = f" {operator} ".join([f"keyword_s:\"{t}\"" for t in keyword_terms])
        query_parts.append(f"({kw_query})")

    # Combine tous les blocs avec AND
    final_query = " AND ".join(query_parts) if query_parts else "*:*"
    return final_query


def search_hal(title_terms=None, abstract_terms=None, keyword_terms=None,
               operator="OR", rows=5, date_from=None, date_until=None):
    """
    Lance une recherche dans HAL avec filtres optionnels par date.
    - date_from : "YYYY-MM-DD"
    - date_until : "YYYY-MM-DD"
    """
    query = build_hal_query(title_terms, abstract_terms, keyword_terms, operator)

    # Filtres de dates
    fq_filters = []
    if date_from and date_until:
        fq_filters.append(f"submittedDate_tdate:[{date_from}T00:00:00Z TO {date_until}T23:59:59Z]")
    elif date_from:
        fq_filters.append(f"submittedDate_tdate:[{date_from}T00:00:00Z TO *]")
    elif date_until:
        fq_filters.append(f"submittedDate_tdate:[* TO {date_until}T23:59:59Z]")

    url = "https://api.archives-ouvertes.fr/search/"
    params = {
        "q": query,
        "fl": "title_s,authFullName_s,uri_s,abstract_s,keyword_s,submittedDate_tdate",
        "rows": rows,
        "wt": "json"
    }

    if fq_filters:
        params["fq"] = fq_filters

    r = requests.get(url, params=params)
    data = r.json()

    for doc in data["response"]["docs"]:
        print("Titre:", doc.get("title_s", ["N/A"])[0])
        print("Auteurs:", ", ".join(doc.get("authFullName_s", [])))
        print("Date dépôt:", doc.get("submittedDate_tdate", "N/A"))
        print("Lien:", doc.get("uri_s", ["N/A"])[0])
        print("Résumé:", doc.get("abstract_s", ["N/A"])[0][:200], "...")
        print("Mots-clés:", ", ".join(doc.get("keyword_s", [])))
        print("-" * 80)


search_hal(
    title_terms=["graph", "network"],
    abstract_terms=["learning", "algorithm"],
    keyword_terms=["optimization"],
    operator="OR",
    rows=5,
    date_from="2020-01-01",
    date_until="2024-12-31"
)