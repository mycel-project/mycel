import logging

from bs4 import BeautifulSoup

from ..cleaner import Cleaner
from src.types.clean_result import CleanResult

logger = logging.getLogger(__name__)


class WikipediaCleaner(Cleaner):
    def __init__(self):
        self.domain = "wikipedia"
    
    def can_clean(self, content: str) -> bool:
        return "mw-parser-output" in content

    def clean(self, content: str) -> CleanResult:
        soup = BeautifulSoup(content, 'lxml')

        infoboxes = soup.find_all("table", class_="infobox")
        
        for infobox in infoboxes:
            self._reserve(infobox)
        
        logger.debug("Found %d infobox(es)", len(infoboxes))

        return CleanResult(
            cleaned_html=str(soup)
        )
