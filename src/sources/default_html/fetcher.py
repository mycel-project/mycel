import requests

from src.utils.url import is_valid_url
from ..fetcher import Fetcher


class DefaultHtmlFetcher(Fetcher):
    def can_fetch(self, source: str) -> bool:
        return is_valid_url(source)

    def fetch(self, source: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(source, headers=headers, timeout=10)
        response.raise_for_status()
        return {"html": response.text}
