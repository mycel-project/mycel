from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from src.models.type_data import TypeData


class NodeSchedulingContext(BaseModel):
    """
    All of data concerning nodes used to process review time
    """
    id: int
    type: Optional[int] = None
    last_review: Optional[int] = None
    type_data: Optional[TypeData] = None
    due: Optional[int] = None
    parent_id: Optional[int] = None
    priority: Optional[str] = None
    overdue: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
