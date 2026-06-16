from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.models.node import NodeStatus, NodeType


class NodeView(BaseModel):
    """
    Lightweight DTO for list display. Contains a short content preview with light fields to allow front side filtering.
    For full content rendering, use NodeDetailView.

    Template Id is passed here and not in DetailView because it's lightweight and the front may want different visualizations based on the template

    There is one due/priority per learning unit attached to this node even if it is not a detailed view. (Could add the same logic for last_reviews)
    """
    id: str
    collection_id: str
    template_id: str 
    type: NodeType
    status: NodeStatus
    updated_at: int
    created_at: int
    content_preview: str 
    dues: list[int]
    priorities: list[float]
    parent_id: Optional[str] = None
    deleted_at: Optional[int] = None


    model_config = ConfigDict(from_attributes=True)
