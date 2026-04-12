from ..contracts import Parent as UnistParent
from . import Comment, Doctype, Element, Text


class Parent(UnistParent):
    children: list

    def __init__(self, children: list):
        self.children = children
        self._validate_children()

    def _validate_children(self) -> None:
        allowed_types = (Comment, Doctype, Element, Text)

        for child in self.children:
            if not isinstance(child, allowed_types):
                raise TypeError(
                    f"Invalid child in Parent: {type(child).__name__}. "
                    f"Allowed: Comment | Doctype | Element | Text"
                )
