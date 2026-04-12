import requests
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.utils.url import is_valid_url
from ..fetcher import Fetcher
from src.types.fetch_result import FetchResult


class DefaultHtmlFetcher(Fetcher):
    def can_fetch(self, source: str) -> bool:
        return is_valid_url(source)

    def fetch(self, source: str) -> FetchResult:
        headers = {
            "User-Agent": self.user_agent
        }

        response = requests.get(source, headers=headers, timeout=10)
        response.raise_for_status()

        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag and title_tag.text else None

        if not title:
            parsed = urlparse(source)
            title = parsed.netloc

        return {
            "html": html,
            "url": source,
            "title": title
        }
