from typing import Optional

from pydantic import BaseModel, field_validator, ConfigDict

from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.type_data import TypeData

class NodeUpdate(BaseModel):
    parent_id: Optional[int] = None
    content: Optional[NodeContent] = None
    data: Optional[NodeData] = None
    type: Optional[int] = None
    due: Optional[int] = None
    priority: Optional[str] = None    
    last_review: Optional[int] = None
    type_data: Optional[TypeData] = None

    @field_validator("type")
    def validate_int_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("Must be positive")
        return v

    @field_validator("content", mode="before") 
    def parse_content(cls, v):
        return NodeContent.from_input(v)

