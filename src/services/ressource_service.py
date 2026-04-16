from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.sources.registry import SourceRegistry


class RessourceService:
    def __init__(self, source_registry: SourceRegistry, html_to_md_registry: HtmlToMdRegistry):
        self._source_registry = source_registry
        self._htm_registry = html_to_md_registry

    def get_ressource_from_url(self, url: str) -> dict:
        fetched = self._source_registry.fetch(url)
        html = fetched.html
        title = fetched.title
        cleaned = self._source_registry.clean(html)
        markdown = self._htm_registry.convert(cleaned.cleaned_html)
        return {"title": title, "markdown": markdown, "source": url, "html": html}
