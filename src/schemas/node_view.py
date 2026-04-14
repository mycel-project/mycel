from pydantic import BaseModel, ConfigDict
from typing import Optional


class NodeView(BaseModel):
    id: int
    collection_id: int
    parent_id: Optional[int] = None
    type: int
    content: Optional[dict] = None
    position: int
    due: int

    model_config = ConfigDict(from_attributes=True)
