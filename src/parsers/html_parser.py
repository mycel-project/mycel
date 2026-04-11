from typing import Optional
from .base_parser import Parser

from html_to_markdown import convert

class HtmlParser(Parser):
    def can_parse(self, content: str, source: Optional[str] = None) -> bool:
        return "<" in content and ">" in content

    def parse(self, content: str) -> str:
        html = content
        markdown = convert(html)

        content = ""
        if markdown and "content" in markdown:
            content = markdown["content"] or "" 

        return content
