import arxiv

query = "(ti:learning OR ti:algorithm OR ti:model OR abs:learning OR abs:algorithm OR abs:model) AND (ti:graph OR ti:network OR abs:graph OR abs:network)"

search = arxiv.Search(
    query=query,
    max_results=5,
    sort_by=arxiv.SortCriterion.Relevance
)

for r in arxiv.Client().results(search):
    print(r.title)
    print("PDF:", r.pdf_url)
    print("-" * 80)
