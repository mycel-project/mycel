from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.models.node import NodeStatus, NodeType


class NodeView(BaseModel):
    """
    Lightweight DTO for list display. Contains a short content preview with light fields to allow front side filtering.
    For full content rendering, use NodeDetailView.
    """
    id: str
    collection_id: str
    template_id: str # Passed here and not in DetailView because it's lightweight and the front may want different visualizations based on the template
    parent_id: Optional[str] = None
    type: NodeType # pulled from base_for
    status: NodeStatus
    updated_at: int
    created_at: int
    deleted_at: Optional[int] = None
    content_preview: Optional[str] = None # data.title or strip
    dues: list[int] # one per learning_unit, 
    priorities: list[int]  # //
    # Could add same logic for last_reviews

    model_config = ConfigDict(from_attributes=True)
