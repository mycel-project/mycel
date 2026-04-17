from pydantic import BaseModel
from typing import Optional


class ReviewContext(BaseModel):
    """
    Review data used by scheduling engine
    """
    id: int
    node_type: int
