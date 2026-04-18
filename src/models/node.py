from pydantic import BaseModel
from typing import Optional

from src.models.node_data import NodeData
from src.types.node_type import NodeType
from .node_content import NodeContent

class Node(BaseModel):
    id: int
    collection_id: int
    created_at: int
    updated_at: int
    data: NodeData
    due: int
    state: int = 1
    content: NodeContent
    type: Optional[int] = NodeType.FRAGMENT
    parent_id: Optional[int] = None
    last_review: Optional[int] = None  
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    step: Optional[int] = None
    priority: Optional[str] = None
