from pydantic import BaseModel, ConfigDict
from typing import Optional

from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.type_data import TypeData


class NodeView(BaseModel):
    """
    To build a DTO containing data used by the frontend
    """
    id: int
    collection_id: int
    parent_id: Optional[int] = None
    type: int
    content: Optional[NodeContent] = None
    position: int
    due: int
    data: Optional[NodeData] = None
    type_data: Optional[TypeData] = None

    model_config = ConfigDict(from_attributes=True)
