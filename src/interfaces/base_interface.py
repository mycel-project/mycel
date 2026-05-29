from abc import ABC, abstractmethod

from src.core.app_infos import AppInfos
from src.core.config import MycelConfig

class BaseInterface(ABC):
    """
    Classe abstraire servant de base pour structurer les interfaces
    """
    def __init__(self, app_infos: AppInfos):
        self.app_infos = app_infos
        
    @abstractmethod
    async def init(self, config: MycelConfig, bus, services, orchestrators):
        pass

    @abstractmethod
    async def start(self):
        pass
