from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from src.models.node import NodeStatus, NodeType
from src.models.node_data import NodeData
from src.schemas.learning_unit_view import LearningUnitView


class NodeView(BaseModel):
    """
    Lightweight DTO for list display. Contains a short content preview with light fields to allow front side filtering.
    For full field rendering, use NodeDetailView.
    """
    id: str
    collection_id: str
    template_id: str 
    type: NodeType
    status: NodeStatus
    updated_at: int
    created_at: int
    content_preview: str
    data: NodeData
    learning_units: list[LearningUnitView] = Field(default_factory=list)  # 1 for fragment but >=1 for spore # If it is too heavy build intermediate models for learningUnits
    parent_id: Optional[str] = None
    deleted_at: Optional[int] = None



    model_config = ConfigDict(from_attributes=True)
