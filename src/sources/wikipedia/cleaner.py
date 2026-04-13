from html_to_markdown import convert

from ..cleaner import Cleaner
from src.types.clean_result import CleanResult


class WikipediaCleaner(Cleaner):
    def can_clean(self, content: str) -> bool:
        return "mw-parser-output" in content


    def clean(self, content: str) -> CleanResult:
        html = content
        markdown = convert(html)

        content = ""
        if markdown and "content" in markdown:
            content = markdown["content"] or "" 

        return CleanResult(
            clean_html=content
        )
