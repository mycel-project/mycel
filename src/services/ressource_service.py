from typing import Optional
from urllib.parse import urlparse


class RessourceService:
    def __init__(self, source_registry):
        self._source_registry = source_registry
    

    def get_ressource_from_url(self, url: str) -> dict:
        fetcher = self._source_registry.get_fetcher(url)
        fetcher.fetch(url)
        parser = self._source_registry.get_parser(url)

        

        if fetcher:
            return fetcher(url)
        
        return self.default_fetch(url)
    
