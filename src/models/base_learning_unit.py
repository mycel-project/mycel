from typing import Optional
from pydantic import BaseModel
from pydantic.config import ConfigDict

class BaseLearningUnit(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    node_id: str
    position: str 
    due: int 
    last_review: Optional[int] = None
