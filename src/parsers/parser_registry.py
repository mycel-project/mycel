from typing import List, Optional
from .base_parser import Parser
from .html_parser import HtmlParser


class ParserRegistry:
    def __init__(self):
        self._parsers: List[Parser] = []
        self._default_parser: Parser = HtmlParser()
        self.register(self._default_parser)

    def register(self, parser: Parser) -> None:
        self._parsers.append(parser)

    def get_parser(self, content: str, source: Optional[str] = None) -> Parser:
        for parser in self._parsers:
            if parser.can_parse(content, source):
                return parser

        return self._default_parser

    def parse(self, content: str, source: Optional[str] = None) -> str:
        parser = self.get_parser(content, source)
        return parser.parse(content)
