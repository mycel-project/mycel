from abc import ABC, abstractmethod

from src.types.clean_result import CleanResult


class Cleaner(ABC):
    @abstractmethod
    def can_clean(self, content: str) -> bool:
        pass
        
    @abstractmethod
    def clean(self, content: str) -> CleanResult:
        pass
