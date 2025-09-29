import arxiv

# Construire une recherche
search = arxiv.Search(
    query="graph theory",
    max_results=5,
    sort_by=arxiv.SortCriterion.SubmittedDate
)

# Exécuter la recherche
for result in arxiv.Client().results(search):
    print("Titre:", result.title)
    print("Auteurs:", [a.name for a in result.authors])
    print("PDF:", result.pdf_url)
    print("-" * 80)
