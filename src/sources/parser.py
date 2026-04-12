from abc import ABC, abstractmethod

from src.types.parse_result import MdParseResult


class Parser(ABC):
    @abstractmethod
    def can_parse(self, content: str) -> bool:
        pass
        
    @abstractmethod
    def parse(self, content: str) -> MdParseResult:
        pass
