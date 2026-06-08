from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

class BaseLearningUnit(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    node_id: str
    position: str 
    due: int 
    last_review: Optional[int] = None
