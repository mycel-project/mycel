from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.type_data import TypeData


class NodeView(BaseModel):
    """
    Lightweight DTO for list display. Contains a short content preview.
    For full content rendering, use NodeDetailView.
    """
    id: str
    collection_id: str
    parent_id: Optional[str] = None
    type: int
    priority: float
    due: int
    deleted_at: Optional[int] = None
    data: Optional[NodeData] = None
    type_data: Optional[TypeData] = None
    content_preview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
