from pydantic import BaseModel
from typing import Optional


class ReviewContext(BaseModel):
    """
    Review data used by scheduling engine
    """
    id: str
    node_type: int
