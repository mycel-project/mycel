from typing import Literal as TypingLiteral
from .literal import Literal

class Text(Literal):
    type: TypingLiteral["text"] = "text" # type: ignore
