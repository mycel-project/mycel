from abc import ABC, abstractmethod

class Parser(ABC):
    @abstractmethod
    def can_parse(self, content: str) -> bool:
        pass
        
    @abstractmethod
    def parse(self, content: str) -> dict:
        pass
