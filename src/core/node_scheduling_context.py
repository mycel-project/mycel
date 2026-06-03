from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from src.models.type_data import TypeData


class NodeSchedulingContext(BaseModel):
    """
    All of data concerning nodes used to process review time
    """
    id: str
    due: int
    type: Optional[int] = None
    last_review: Optional[int] = None
    type_data: Optional[TypeData] = None
    parent_id: Optional[str] = None
    position: Optional[str] = None
    overdue: Optional[int] = None
    encounter_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
