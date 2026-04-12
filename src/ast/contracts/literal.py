from typing import Any
from .node import Node

class Literal(Node):
    value: Any | None = None
