from abc import ABC, abstractmethod

class BaseInterface(ABC):
    """
    Classe abstraire servant de base pour structurer les interfaces
    """
    @abstractmethod
    async def init(self, config: dict, bus, services):
        pass

    @abstractmethod
    async def start(self):
        pass
