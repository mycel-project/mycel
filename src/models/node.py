from pydantic import BaseModel, ConfigDict, model_validator
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
    model_config = ConfigDict(validate_assignment=True)
    id: str
    collection_id: str
    created_at: int
    updated_at: int
    data: NodeData
    due: int
    content: NodeContent
    position: str 
    type: NodeType = NodeType.FRAGMENT
    type_data: TypeData
    deleted_at: Optional[int] = None
    parent_id: Optional[str] = None
    last_review: Optional[int] = None  

    
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

    @classmethod
    def from_db(cls, row: dict) -> 'Node':
        row_dict = dict(row) if hasattr(row, 'keys') else row.__dict__
        
        return cls(
            id=row_dict["id"],
            collection_id=row_dict["collection_id"],
            parent_id=row_dict["parent_id"],
            type=row_dict["type"],
            created_at=row_dict["created_at"],
            updated_at=row_dict["updated_at"],
            deleted_at=row_dict["deleted_at"],
            data=NodeData.from_db(row_dict["data"]),
            due=row_dict["due"],
            content=NodeContent.from_db(row_dict["content"]),
            last_review=row_dict["last_review"],
            type_data=row_dict["type_data"],
            position=row_dict["position"],
        )
