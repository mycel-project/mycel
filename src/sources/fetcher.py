from abc import ABC, abstractmethod

class Fetcher(ABC):
    def __init__(self, user_agent = None):
        self.user_agent = user_agent

    @abstractmethod
    def can_fetch(self, source: str) -> bool:
        pass
        
    @abstractmethod
    def fetch(self, source: str) -> dict:
        pass
