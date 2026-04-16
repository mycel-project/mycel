import logging
from collections import defaultdict

from bs4 import BeautifulSoup, Tag

from ..cleaner import Cleaner
from src.types.clean_result import CleanResult

logger = logging.getLogger(__name__)

REMOVE_TAGS = [
    'script', 'style', 'meta', 'noscript', 'nav', 'footer', 'iframe', 'ads', 'table'
]

class DefaultHtmlCleaner(Cleaner):
    def can_clean(self, content: str) -> bool:
        return "<html" in content.lower() or "<div" in content.lower()

    def clean(self, content: str) -> CleanResult:
        soup = BeautifulSoup(content, 'lxml')

        reserved_counts = defaultdict(int)
        
        cleaned_counts = defaultdict(int)
        cleaned_element_tags = []
        
        for tag_name in REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                if not hasattr(tag, "attrs") or tag.attrs is None:
                    tag.attrs = {}
                if self._is_reserved(tag):
                    reserved_counts[tag_name] += 1
                    continue
                cleaned_element_tags.append(tag_name)
                cleaned_counts[tag_name] += 1
                tag.decompose()

        logger.debug(f"Tag removal summary: {dict(cleaned_counts)}. Reserved tags : {dict(reserved_counts)}")
        
        cleaned_html = str(soup.prettify())

        return CleanResult(
            cleaned_html=cleaned_html
        )
