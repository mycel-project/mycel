import importlib
from typing import List

from .fetcher import Fetcher
from .parser import Parser
from .sources_config import SOURCES_ORDER


class SourceRegistry:
    def __init__(self, user_agent):
        self._fetchers: List[Fetcher] = []
        self._parsers: List[Parser] = []
        
        self._default_fetcher: Fetcher | None = None
        self._default_parser: Parser | None = None

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
                    issubclass(attr, Parser) and 
                    attr is not Parser):
                    parser = attr()
                    self.register_parser(parser, is_default=(source_name == "default_html"))
        
        except ImportError as e:
            raise ImportError(f"Error while loading source '{source_name}': {e}")

    def _validate_defaults(self) -> None:
        if self._default_fetcher is None:
            raise RuntimeError(
                f"No default fetcher defined."
            )
        if self._default_parser is None:
            raise RuntimeError(
                f"No default parser defined."
            )

    def register_fetcher(self, fetcher: Fetcher, is_default: bool = False) -> None:
        self._fetchers.append(fetcher)
        if is_default:
            self._default_fetcher = fetcher

    def register_parser(self, parser: Parser, is_default: bool = False) -> None:
        self._parsers.append(parser)
        if is_default:
            self._default_parser = parser

    def get_fetcher(self, source: str) -> Fetcher:
        for fetcher in self._fetchers:
            if fetcher.can_fetch(source):
                return fetcher
        assert self._default_fetcher != None
        return self._default_fetcher

    def fetch(self, source: str) -> dict:
        fetcher = self.get_fetcher(source)
        return fetcher.fetch(source)

    def get_parser(self, content: str) -> Parser:
        for parser in self._parsers:
            if parser.can_parse(content):
                return parser
        assert self._default_parser != None
        return self._default_parser

    def parse(self, content: str) -> dict:
        parser = self.get_parser(content)
        return parser.parse(content)
