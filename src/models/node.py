import json
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
from typing import Optional

from src.models.fragment import Fragment
from src.models.learning_unit import LearningUnit
from src.models.node_data import NodeData
from src.models.spore import Spore
from src.utils.time import now_ms

class NodeFields(RootModel[dict[str, str]]):
    def __getitem__(self, key: str) -> str:
        return self.root[key]
    def __setitem__(self, key: str, value: str) -> None:
        self.root[key] = value
    def __contains__(self, key: str) -> bool:
        return key in self.root
    def get_preview(self, length: int = 150) -> Optional[str]:
        if not self.root:
            return None
        first_value = next(iter(self.root.values()))
        return first_value[:length]

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "NodeFields":
        return cls(root=data)
    def get_content(self) -> Optional[str]:
        return self.root.get("content")

class NodeType(str, Enum):
    FRAGMENT = "fragment"
    SPORE = "spore"

class NodeStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    
class Node(BaseModel):
    """
    Domain model gathering data related to a node and his learning units.
    """
    # Note: "spore" and "fragment" in args refer to learning unit ids, not node ids.
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
    learning_units: list[LearningUnit] = Field(default_factory=list)

    @field_validator("fields", "data", mode="before")
    @classmethod
    def deserialize_json_strings(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v

    def get_fragment(self) -> Fragment:
        if self.base_for != NodeType.FRAGMENT:
            raise ValueError(f"Cannot access fragment on a node of type {self.base_for}")
        if not self.learning_units:
            raise RuntimeError("Node has not been hydrated yet.")
        unit = self.learning_units[0]
        if not isinstance(unit, Fragment):
            raise RuntimeError(f"Expected Fragment, got {type(unit)}")
        return unit

    def get_unit(self, unit_id: str) -> LearningUnit:
        unit = next((u for u in self.learning_units if u.id == unit_id), None)
        if unit is None:
            raise RuntimeError(f"Unit {unit_id} not found on node {self.id}")
        return unit

    def get_unit_by_slot(self, slot: int = 0) -> LearningUnit:
        unit = next((u for u in self.learning_units if getattr(u, 'slot', 0) == slot), None)
        if unit is None:
            raise RuntimeError(f"No unit found for slot {slot} on node {self.id}")
        return unit

    def get_spore(self, unit_id: str) -> Spore:
        unit = self.get_unit(unit_id)
        if not isinstance(unit, Spore):
            raise RuntimeError(f"Unit {unit_id} is not a Spore")
        return unit
