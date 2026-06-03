import json

from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional

from src.models.node_state_before import NodeStateBefore
from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.types.node_type import NodeType

TYPE_REVIEW_DATA_MAP = {
    NodeType.SPORE: SporeReviewData,
    NodeType.FRAGMENT: FragmentReviewData,
}

class Review(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: str
    node_id: str
    type: NodeType = NodeType.FRAGMENT
    time: int
    type_review_data: TypeReviewData
    duration: Optional[int] = None
    node_state_before: NodeStateBefore

    @model_validator(mode="before")
    @classmethod
    def build_typed_fields(cls, values):
        node_type = values.get("type")

        # type_review_data
        raw = values.get("type_review_data")
        factory = TYPE_REVIEW_DATA_MAP.get(node_type)
        if factory is None:
            raise ValueError(f"Unknown node type: {node_type}")
        if raw is None:
            values["type_review_data"] = factory()
        else:
            if isinstance(raw, str):
                raw = json.loads(raw)
            values["type_review_data"] = factory.model_validate(raw)

        # node_state_before
        raw_snapshot = values.get("node_state_before")
        if isinstance(raw_snapshot, str):
            raw_snapshot = json.loads(raw_snapshot)
        if isinstance(raw_snapshot, dict):
            values["node_state_before"] = NodeStateBefore.from_dict(raw_snapshot, NodeType(node_type))

        return values
