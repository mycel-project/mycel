from urllib.parse import urlparse, unquote

import requests

from ..fetcher import Fetcher
from src.types.fetch_result import FetchResult


class WikipediaFetcher(Fetcher):
    def can_fetch(self, source: str) -> bool:
        return "wikipedia.org" in source

    def fetch(self, source: str) -> FetchResult:
        netloc, path = self.parse_url(source)
        endpoint = '/with_html'
        base_url = f'https://{netloc}/w/rest.php/v1/page/'
        url = base_url + path + endpoint
        headers = {
            "User-Agent": self.user_agent
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        html = data["html"]
        title = data["title"]
        
        return FetchResult(
            html=html,
            url=url,
            title=title
        )

    def parse_url(self, url: str) -> tuple[str, str]:
        try:
            parsed_url = urlparse(url)
            netloc = parsed_url.netloc

            if "wikipedia.org" not in netloc:
                raise ValueError("URL does not contain wikipedia.org")
            
            path_parts = parsed_url.path.split("/")
            if "wiki" not in path_parts:
                raise ValueError("URL does not contain '/wiki/' section")
            
            wiki_index = path_parts.index("wiki")
            if wiki_index + 1 >= len(path_parts):
                raise ValueError("No '/wiki/' section")
            
            path = path_parts[wiki_index + 1]
            path = unquote(path)
            return netloc, path
        except Exception as e:
            raise ValueError(f"Error while extracting wikipedia path: {e}")
