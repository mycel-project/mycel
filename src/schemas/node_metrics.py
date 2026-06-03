from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from src.models.type_data import TypeData


class NodeMetrics(BaseModel): # sending some of those things in NodeView (as type_data for fragments)
    """
    Intended for UI usage
    """
    id: str
    last_review: Optional[int] = None
    type_data: Optional[TypeData] = None
    encounter_count: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

