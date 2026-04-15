from src.types.html_content import HtmlContent
from src.types.md_content import MdContent


class WikipediaConverter:
    domain = "wikipedia"

    def convert(self, html: HtmlContent) -> MdContent:
        print("test!!")
        markdown = html
        return MdContent(markdown)
