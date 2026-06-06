import requests

from abc import ABC, abstractmethod

from src.domain.domain_exceptions import PageTooLarge
from src.types.fetch_result import FetchResult


class Fetcher(ABC):
    def __init__(self, user_agent = None):
        self.user_agent = user_agent
        self.MAX_SIZE = 2 * 1024 * 1024 # 1MB

    @abstractmethod
    def can_fetch(self, source: str) -> bool:
        pass
        
    @abstractmethod
    def fetch(self, source: str) -> FetchResult:
        pass

    def safe_get(self, url: str, timeout: int = 10, **kwargs) -> requests.Response:
        response = requests.get(url, stream=True, timeout=timeout, **kwargs)
        response.raise_for_status()
        content = b""
        for chunk in response.iter_content(8192):
            content += chunk
            if len(content) > self.MAX_SIZE:
                raise PageTooLarge(url, self.MAX_SIZE)
        response._content = content
        return response
