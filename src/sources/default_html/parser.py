from html_to_markdown import convert

from ..parser import Parser
from src.types.parse_result import MdParseResult


class DefaultHtmlParser(Parser):
    def can_parse(self, content: str) -> bool:
        return "<html" in content.lower() or "<div" in content.lower()

    def parse(self, content: str) -> MdParseResult:
        html = content
        markdown = convert(html)

        content = ""
        if markdown and "content" in markdown:
            content = markdown["content"] or "" 

        return {"md": content}
