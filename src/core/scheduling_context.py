from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.models.node import NodeType

class SchedulingContext(BaseModel):
    """
    All of data concerning nodes used to process review time
    """
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)

    id: str
    due: int
    type: Optional[NodeType] = None
    last_review: Optional[int] = None
    parent_id: Optional[str] = None
    position: Optional[str] = None
    overdue: Optional[int] = None
    encounter_count: Optional[int] = None
    dismiss: Optional[bool] = None
