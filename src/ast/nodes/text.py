from typing import Literal as TypingLiteral
from . import Literal

class Text(Literal):
    type: TypingLiteral["text"] = "text" # type: ignore
