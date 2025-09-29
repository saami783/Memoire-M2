import arxiv

query = "(ti:graph OR abs:graph) AND (ti:learning OR abs:learning)"

search = arxiv.Search(
    query=query,
    max_results=5,
    sort_by=arxiv.SortCriterion.Relevance
)

for r in arxiv.Client().results(search):
    print(r.title)
    print("PDF:", r.pdf_url)
    print("-" * 80)
