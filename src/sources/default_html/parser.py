from html_to_markdown import convert

from ..parser import Parser


class DefaultHtmlParser(Parser):
    def can_parse(self, content: str) -> bool:
        return "<html" in content.lower() or "<div" in content.lower()

    def parse(self, content: str) -> dict:
        html = content
        markdown = convert(html)

        content = ""
        if markdown and "content" in markdown:
            content = markdown["content"] or "" 

        return {"content": content}
