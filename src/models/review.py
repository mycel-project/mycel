from pydantic import BaseModel, model_validator
from typing import Optional

from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.types.node_type import NodeType

TYPE_REVIEW_DATA_MAP = {
    NodeType.SPORE: SporeReviewData,
    NodeType.FRAGMENT: FragmentReviewData,
}

class Review(BaseModel):
    id: int
    node_id: int
    type: NodeType = NodeType.FRAGMENT
    time: int
    type_review_data: TypeReviewData
    duration: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def build_type_review_data(cls, values):
        raw = values.get("type_review_data")
        node_type = values.get("type")

        factory = TYPE_REVIEW_DATA_MAP.get(node_type)
        if factory is None:
            raise ValueError(f"Unknown node type: {node_type}")

        if raw is None:
            values["type_review_data"] = factory()
            return values

        if isinstance(raw, str):
            import json
            raw = json.loads(raw)

        values["type_review_data"] = factory.model_validate(raw)

        return values
