from src.converters.html_to_md.profile import Profile
#from html_to_markdown import convert as md_convert
from markdownify import markdownify as md

from src.types.md_content import MdContent


class GenericConverter(Profile):
    domain = "generic"

    def convert(self, html: str) -> MdContent:
        markdown = md(html)
        return MdContent(markdown["content"])
