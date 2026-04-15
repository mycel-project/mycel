from dataclasses import dataclass

from src.types.html_content import HtmlContent


@dataclass
class CleanResult:
    cleaned_html: HtmlContent
