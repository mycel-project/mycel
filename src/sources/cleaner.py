from abc import ABC, abstractmethod

from src.types.clean_result import CleanResult


class Cleaner(ABC):
    @abstractmethod
    def can_clean(self, content: str) -> bool:
        pass
        
    @abstractmethod
    def clean(self, content: str) -> CleanResult:
        pass

    def _is_reserved(self, tag):
        return tag.has_attr("mycel-cleaner-name")

    def _reserve(self, tag):
        tag["mycel-cleaner-name"] = self.__class__.__name__
        
