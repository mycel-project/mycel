from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.models.node_content import NodeContent
from src.models.node_data import NodeData


class NodeView(BaseModel):
    id: int
    collection_id: int
    parent_id: Optional[int] = None
    type: int
    content: Optional[NodeContent] = None
    position: int
    due: int
    data: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
