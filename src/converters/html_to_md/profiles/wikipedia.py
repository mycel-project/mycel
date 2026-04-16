from src.converters.html_to_md.profile import Profile
from src.types.md_content import MdContent
from html_to_markdown import convert as md_convert


class WikipediaConverter(Profile):
    domain = "wikipedia"

    def convert(self, html: str) -> MdContent:
        markdown = md_convert(html)
        return MdContent(markdown["content"])
