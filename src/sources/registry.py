import importlib
from typing import List

from src.types.fetch_result import FetchResult
from src.types.clean_result import CleanResult

from .fetcher import Fetcher
from .cleaner import Cleaner
from .sources_config import SOURCES_ORDER


class SourceRegistry:
    def __init__(self, user_agent):
        self._fetchers: List[Fetcher] = []
        self._cleaners: List[Cleaner] = []
        
        self._default_fetcher: Fetcher | None = None
        self._default_cleaner: Cleaner | None = None

        self._load_sources(user_agent)
        self._validate_defaults()

    def _load_sources(self, user_agent: str) -> None:
        for source_name in SOURCES_ORDER:
            self._load_source(source_name, user_agent)

    def _load_source(self, source_name: str, user_agent: str) -> None:
        try:
            module = importlib.import_module(f".{source_name}", package=__package__)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (isinstance(attr, type) and 
                    issubclass(attr, Fetcher) and 
                    attr is not Fetcher):
                    fetcher = attr(user_agent)
                    self.register_fetcher(fetcher, is_default=(source_name == "default_html"))
                
                if (isinstance(attr, type) and 
                    issubclass(attr, Cleaner) and 
                    attr is not Cleaner):
                    cleaner = attr()
                    self.register_cleaner(cleaner, is_default=(source_name == "default_html"))
        
        except ImportError as e:
            raise ImportError(f"Error while loading source '{source_name}': {e}")

    def _validate_defaults(self) -> None:
        if self._default_fetcher is None:
            raise RuntimeError(
                f"No default fetcher defined."
            )
        if self._default_cleaner is None:
            raise RuntimeError(
                f"No default cleaner defined."
            )

    def register_fetcher(self, fetcher: Fetcher, is_default: bool = False) -> None:
        self._fetchers.append(fetcher)
        if is_default:
            self._default_fetcher = fetcher

    def register_cleaner(self, cleaner: Cleaner, is_default: bool = False) -> None:
        self._cleaners.append(cleaner)
        if is_default:
            self._default_cleaner = cleaner

    def get_fetcher(self, source: str) -> Fetcher:
        for fetcher in self._fetchers:
            if fetcher.can_fetch(source):
                return fetcher
        assert self._default_fetcher != None
        return self._default_fetcher

    def fetch(self, source: str) -> FetchResult:
        fetcher = self.get_fetcher(source)
        return fetcher.fetch(source)

    def get_cleaners(self, content: str) -> List[Cleaner]:
        applicable_cleaners = []

        for cleaner in self._cleaners:
            if cleaner.can_clean(content):
                applicable_cleaners.append(cleaner)

        if self._default_cleaner not in applicable_cleaners:
            applicable_cleaners.append(self._default_cleaner)

        return applicable_cleaners

    def clean(self, content: str) -> CleanResult:
        cleaners = self.get_cleaners(content)
        current_content = content

        for cleaner in cleaners:
            result = cleaner.clean(current_content)
            current_content = result.clean_html

        return result
