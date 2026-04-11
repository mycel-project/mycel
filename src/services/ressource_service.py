from typing import Optional
import requests
from urllib.parse import urlparse, unquote


class RessourceService:
    """
    Parse to markdown
    """
    def __init__(self, user_agent):
        self.user_agent = user_agent
        pass

    def fetch_ressource(self, ressource):
        pass

    def fetch_from_url(self, url: str) -> str:
        """Fetch HTML content from URL."""
        parsed_url = urlparse(url)

        if "wikipedia.org" in parsed_url.netloc:
            self.fetch_from_wikipedia(url)
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL: {e}")
            

    def fetch_from_wikipedia(self, url: str) -> str:
        """
        Extrait le titre d'une page Wikipedia à partir de son URL.
        Exemple: https://en.wikipedia.org/wiki/Artificial_intelligence#History
        Retourne: "Artificial_intelligence"
        """
        netloc, title = self.parse_wikipedia_url(url)
        url = f"https://{netloc}/api/rest_v1/page/title/{title}"
        headers = {
            'User-Agent': self.user_agent
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        return "ok"


    def parse_wikipedia_url(self, url: str) -> tuple[str,str]:
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
            
            title = path_parts[wiki_index + 1]
            title = unquote(title)
            return netloc, title
        except Exception as e:
            raise ValueError(f"Error while extracting wikipedia title: {e}")
            
