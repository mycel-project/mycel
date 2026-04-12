from typing import Optional
from urllib.parse import urlparse


class RessourceService:
    def __init__(self, source_registry):
        self._source_registry = source_registry
    

    def get_ressource_from_url(self, url: str) -> dict:
        fetcher = self._source_registry.get_fetcher(url)
        fetched = fetcher.fetch(url)
        html = fetched["html"]
        title = fetched["title"]
        parser = self._source_registry.get_parser(html)
        parsed = parser.parse(html)
        return {"title": title, "markdown": parsed["md"], "source": url}

