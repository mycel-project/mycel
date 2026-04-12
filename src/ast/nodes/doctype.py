from typing import Literal as TypingLiteral
from ..contracts import Node

class Doctype(Node):
    type: TypingLiteral["doctype"] = "doctype" # type: ignore
