from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from src.models.type_data import TypeData


class NodeMetrics(BaseModel):
    """
    Intended for UI usage
    """
    id: int
    last_review: Optional[int] = None
    type_data: Optional[TypeData] = None
    encounter_count: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

