from pydantic import BaseModel, ConfigDict
from typing import Optional


class NodeSchedulingContext(BaseModel):
    """
    All of data concerning nodes used to process review time
    """
    id: int
    type: Optional[int] = None
    last_review: Optional[int] = None
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    due: Optional[int] = None
    parent_id: Optional[int] = None
    priority: Optional[str] = None
    overdue: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
