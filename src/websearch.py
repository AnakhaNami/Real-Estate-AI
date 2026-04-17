from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 4) -> str:
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(
                query + " Kerala real estate India",
                max_results=max_results
            ):
                results.append(f"Source: {r['href']}\n{r['title']}: {r['body']}")
        if not results:
            return "No web results found."
        return "\n\n".join(results)
    except Exception as e:
        return f"Web search unavailable: {str(e)}"