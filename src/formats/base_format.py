from abc import ABC, abstractmethod
from typing import Pattern

from src.models.outline import Outline


class BaseFormat(ABC):
    id: str # required

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "id"):
            raise TypeError(f"No id field found for {cls.__name__}")

    @property
    def heading_pattern(self) -> Pattern[str] | None:
        return None

    @property
    def extract_emphasis_pattern(self) -> Pattern[str] | None:
        return None

    def get_outline(self, text: str) -> Outline:
        """
        To generate an outline for the text passed in args.

        If not implented: return empty outline.
        """
        return Outline(entries=[])
