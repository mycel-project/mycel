from typing import Literal as TypingLiteral
from .parent import Parent

class Root(Parent):
    type: TypingLiteral["root"] = "root" # type: ignore

