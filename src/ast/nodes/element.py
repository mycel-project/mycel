from typing import Literal as TypingLiteral, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .root import Root

from .parent import Parent
from ..contracts import Properties


class Element(Parent):
    type: TypingLiteral["element"] = "element"  # type: ignore
    tagName: str
    properties: Properties
    content: Optional["Root"] = None

 
