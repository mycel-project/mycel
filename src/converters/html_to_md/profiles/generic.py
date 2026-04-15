from src.converters.html_to_md.profile import Profile
from html_to_markdown import convert as md_convert

from src.types.html_content import HtmlContent
from src.types.md_content import MdContent


class GenericConverter(Profile):
    domain = "generic"

    def convert(self, html: HtmlContent) -> MdContent:
        markdown = md_convert(html)
        return MdContent(markdown["content"])
