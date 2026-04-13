from bs4 import BeautifulSoup

from ..cleaner import Cleaner
from src.types.clean_result import CleanResult

REMOVE_TAGS = [
    'script', 'style', 'meta', 'noscript', 'nav', 'footer', 'iframe', 'ads'
]

class DefaultHtmlCleaner(Cleaner):
    def can_clean(self, content: str) -> bool:
        return "<html" in content.lower() or "<div" in content.lower()

    def clean(self, content: str) -> CleanResult:
        soup = BeautifulSoup(content, 'lxml')
        
        for tag_name in REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        cleaned_html = str(soup.prettify())

        return CleanResult(
            cleaned_html=cleaned_html
        )
