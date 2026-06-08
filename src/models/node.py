import json
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
from typing import Optional, TypeAlias

from src.models.node_data import NodeData
from src.utils.time import now_ms

class NodeFields(RootModel[dict[str, str]]):
    pass

class NodeType(str, Enum):
    FRAGMENT = "fragment"
    SPORE = "spore"

class NodeStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    
class Node(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    collection_id: str
    template_id: str
    created_at: int = Field(default_factory=lambda: now_ms())
    updated_at: int = Field(default_factory=lambda: now_ms())
    base_for: NodeType
    fields: NodeFields
    data: NodeData = Field(default_factory=NodeData)  
    status: NodeStatus = NodeStatus.ACTIVE
    deleted_at: Optional[int] = None
    parent_id: Optional[str] = None

    @field_validator("fields", "data", mode="before")
    @classmethod
    def deserialize_json_strings(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v
