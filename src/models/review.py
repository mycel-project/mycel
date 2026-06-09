import json

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

from src.models.learning_unit import LearningUnit
from src.models.node import NodeType
from src.models.type_review_data import TypeReviewData


class Review(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: str
    learning_unit_id: str
    type: NodeType = NodeType.FRAGMENT
    reviewed_at: int
    type_review_data: TypeReviewData # Data specific to the type of learning unit
    duration: Optional[int] = None
    state_before: LearningUnit

    @field_validator("type_review_data", "state_before", mode="before")
    @classmethod
    def deserialize_json_strings(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v
