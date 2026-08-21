from abc import ABC
from typing import Pattern

from src.models.outline import Outline


class BaseFormat(ABC):
    """
    Unimplemented methods do not raise errors when called, but the user will receive no feedback for the corresponding action.
    """
    id: str # required

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "id"):
            raise TypeError(f"No id field found for {cls.__name__}")

    # --- OUTLINE ---
    
    def get_outline(self, text: str) -> Outline:
        """
        Generates an outline from the provided text content.
        
        Returns an Outline object containing the hierarchical structure of the document.
        If not implemented returns an empty Outline.
        """
        return Outline(entries=[])

    # --- FRAGMENT EMPHASIS ---

    @property
    def fragment_emphasis_pattern(self) -> Pattern[str] | None:
        """Regex pattern matching the emphasis used when extracting to a Fragment."""
        return None

    def apply_fragment_emphasis(self, text: str) -> str:
        """Applies the format-specific emphasis for extracted Fragments."""
        return text
        
    def remove_fragment_emphasis(self, text: str, allowed_prefix_pattern: str | None = None) -> str:
        """Removes the format-specific emphasis for extracted Fragments."""
        return text

    # --- SPORE EMPHASIS ---

    @property
    def spore_emphasis_pattern(self) -> Pattern[str] | None:
        """Regex pattern matching the emphasis used when extracting to a Spore."""
        return None

    def apply_spore_emphasis(self, text: str) -> str:
        """Applies the format-specific emphasis for extracted Spores."""
        return text

    def remove_spore_emphasis(self, text: str) -> str:
        """Removes the format-specific emphasis for extracted Spores."""
        return text

    # --- LINKS ---

    def strip_links(self, text: str) -> str:
        """Removes hyperlinks formatting, keeping only the anchor text."""
        return text
