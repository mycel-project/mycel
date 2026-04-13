from src.sources.registry import SourceRegistry


class RessourceService:
    def __init__(self, source_registry: SourceRegistry):
        self._source_registry = source_registry
    

    def get_ressource_from_url(self, url: str) -> dict:
        fetched = self._source_registry.fetch(url)
        html = fetched.html
        title = fetched.title
        cleaned = self._source_registry.clean(html)
        return {"title": title, "markdown": cleaned.cleaned_html, "source": url, "html": html}
