from typing import Literal as TypingLiteral, Optional
from . import Parent, Comment, Text, Root
from ..contracts import Properties


class Element(Parent):
    type: TypingLiteral["element"] = "element"  # type: ignore

    tagName: str
    properties: Properties
    content: Optional[Root] = None

    def __init__(
        self,
        tagName: str,
        properties: Properties,
        children: list,
        content: Optional[Root] = None,
    ):
        self.tagName = tagName
        self.properties = properties
        self.children = children
        self.content = content

        self._validate_children()

    def _validate_children(self) -> None:
        allowed_types = (Comment, Text, Element)

        for child in self.children:
            if not isinstance(child, allowed_types):
                raise TypeError(
                    f"Invalid child in Element: {type(child).__name__}. "
                    f"Allowed: Comment | Text | Element"
                )
