from pydantic import BaseModel
from typing import Optional


class NodeMetrics(BaseModel):
    id: int
    last_review: Optional[int] = None
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    state: int
    step: Optional[int] = None

    class Config:
        from_attributes = True
