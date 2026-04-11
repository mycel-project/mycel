from abc import ABC, abstractmethod
from typing import Optional


class Parser(ABC):
    @abstractmethod
    def can_parse(self, content: str, source: Optional[str] = None) -> bool:
        """
        Determine if this parser can handle the given content.
        """
        pass

    @abstractmethod
    def parse(self, content: str) -> str:
        pass
