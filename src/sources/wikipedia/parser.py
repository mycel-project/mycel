from html_to_markdown import convert

from ..parser import Parser
from src.types.parse_result import MdParseResult


class WikipediaParser(Parser):
    def can_parse(self, content: str) -> bool:
        return "mw-parser-output" in content

    def parse(self, content: str) -> MdParseResult:
        html = content
        markdown = convert(html)

        content = ""
        if markdown and "content" in markdown:
            content = markdown["content"] or "" 

        return {"md": content}
