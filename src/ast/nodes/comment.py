from typing import Literal as TypingLiteral
from .literal import Literal

class Comment(Literal):
    type: TypingLiteral["comment"] = "comment" # type: ignore
