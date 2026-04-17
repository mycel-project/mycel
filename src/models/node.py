from pydantic import BaseModel
from typing import Optional

from src.models.node_data import NodeData
from .node_content import NodeContent

NEW        = 0
LEARNING   = 1
REVIEW     = 2
RELEARNING = 3

class Node(BaseModel):
    id: int
    collection_id: int
    type: int = NEW 
    created_at: int
    updated_at: int
    data: NodeData
    due: int
    state: int = 1
    content: NodeContent
    parent_id: Optional[int] = None
    last_review: Optional[int] = None  
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    step: Optional[int] = None
    priority: Optional[str] = None
