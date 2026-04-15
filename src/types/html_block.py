from dataclasses import dataclass

from src.types.html_content import HtmlContent

@dataclass
class HtmlBlock:
    domain: str
    node: HtmlContent
