from pydantic import BaseModel
from typing import Optional

from .data import Data
from .position import Position


class Node(BaseModel):
    type: str
    data: Optional[Data] = None
    position: Optional[Position] = None
