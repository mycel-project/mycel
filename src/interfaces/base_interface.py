from abc import ABC, abstractmethod

from src.core.app_infos import AppInfos

class BaseInterface(ABC):
    """
    Classe abstraire servant de base pour structurer les interfaces
    """
    @abstractmethod
    async def init(self, config: dict, bus, app_infos: AppInfos, services, orchestrators):
        pass

    @abstractmethod
    async def start(self):
        pass
