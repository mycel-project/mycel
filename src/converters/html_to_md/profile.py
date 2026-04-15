from abc import ABC, abstractmethod

from src.types.html_content import HtmlContent
from src.types.md_content import MdContent


class Profile(ABC):
    """
    Base class for HTML → Markdown conversion profiles.

    Each profile implements a specific conversion strategy
    """
    domain: str
    
    @abstractmethod
    def convert(self, html: HtmlContent) -> MdContent:
        pass

