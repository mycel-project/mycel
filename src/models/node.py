from pydantic import BaseModel, model_validator
from typing import Optional
import json

from src.models.node_data import NodeData
from src.models.type_data import TypeData
from src.models.type_data.fragment_data import FragmentData
from src.models.type_data.spore_data import SporeData
from src.types.node_type import NodeType
from .node_content import NodeContent

TYPE_DATA_MAP = {
    NodeType.SPORE: SporeData,
    NodeType.FRAGMENT: FragmentData,
}


class Node(BaseModel):
    id: int
    collection_id: int
    created_at: int
    updated_at: int
    data: NodeData
    due: int
    content: NodeContent
    type: NodeType = NodeType.FRAGMENT
    type_data: TypeData
    parent_id: Optional[int] = None
    last_review: Optional[int] = None  
    priority: Optional[str] = None


    @model_validator(mode="before")
    @classmethod
    def build_type_data(cls, values):
        raw = values.get("type_data")
        node_type = values.get("type")

        factory = TYPE_DATA_MAP.get(node_type)
        if factory is None:
            raise ValueError(f"Unknown node type: {node_type}")

        if raw is None:
            values["type_data"] = factory()
            return values

        if isinstance(raw, str):
            import json
            raw = json.loads(raw)

        values["type_data"] = factory.model_validate(raw)

        return values
