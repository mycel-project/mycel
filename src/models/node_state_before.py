from typing import Optional
from pydantic import BaseModel
from src.models.node import TYPE_DATA_MAP
from src.models.type_data import TypeData
from src.types.node_type import NodeType


class NodeStateBefore(BaseModel):
    due: int
    last_review: Optional[int] = None
    type_data: TypeData

    @classmethod
    def from_dict(cls, data: dict, node_type: NodeType) -> "NodeStateBefore":
        model = TYPE_DATA_MAP.get(node_type)
        if model:
            data["type_data"] = model(**data["type_data"])
        return cls(**data)
