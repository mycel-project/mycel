from pydantic import BaseModel
from typing import Optional


class NodeView(BaseModel):
    id: int
    collection_id: int
    type: int
    content: Optional[dict] = None
    position: int
    due: int

    class Config:
        from_attributes = True
