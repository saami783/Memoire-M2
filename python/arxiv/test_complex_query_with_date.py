import arxiv

query = "(ti:graph OR abs:graph) AND (ti:learning OR abs:learning) AND submittedDate:[20220101 TO 20231231]"

search = arxiv.Search(
    query=query,
    max_results=5,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

for r in arxiv.Client().results(search):
    print(r.published.date(), "-", r.title)
    print("PDF:", r.pdf_url)
    print("-" * 80)
