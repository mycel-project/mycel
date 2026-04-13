from html_to_markdown import convert

from ..cleaner import Cleaner
from src.types.clean_result import CleanResult


class DefaultHtmlCleaner(Cleaner):
    def can_clean(self, content: str) -> bool:
        return "<html" in content.lower() or "<div" in content.lower()

    def clean(self, content: str) -> CleanResult:
        html = content

        return CleanResult(
            clean_html=content
        )
