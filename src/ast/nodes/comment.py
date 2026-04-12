from typing import Literal as TypingLiteral
from . import Literal

class Comment(Literal):
    type: TypingLiteral["comment"] = "comment" # type: ignore
