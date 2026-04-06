from .registry import INTERFACE_REGISTRY
from .base_interface import BaseInterface

class InterfaceFactory:
    @staticmethod
    def create(name) -> BaseInterface:
        cls = INTERFACE_REGISTRY.get(name)
        if not cls:
            raise ValueError(f"Unknown interface: {name}")
        return cls()
