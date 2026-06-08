from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, TypeAlias

from src.models.node_data import NodeData

NodeFields: TypeAlias = dict[str, str]

class NodeType(str, Enum):
    FRAGMENT = "fragment"
    SPORE = "spore"

class NodeStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    
class Node(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: str
    collection_id: str
    template_id: str
    created_at: int
    updated_at: int
    base_for: NodeType
    fields: NodeFields
    data: NodeData = Field(default_factory=NodeData)  
    status: NodeStatus = NodeStatus.ACTIVE
    deleted_at: Optional[int] = None
    parent_id: Optional[str] = None
