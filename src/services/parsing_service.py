from src.parsers import ParserRegistry
from typing import Optional


class ParsingService:
    """
    Parse to markdown
    """
    def __init__(self, parser_registry: ParserRegistry):
        self._parser_registry = parser_registry

    def parse_content(self, content: str, source: Optional[str] = None) -> str:
        return self._parser_registry.parse(content, source)
