from pydantic import BaseModel
from typing import Optional


class Review(BaseModel):
    id: int
    node_id: int
    time: int
    duration: Optional[int] = None
    rating: int
