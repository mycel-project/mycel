from typing import Optional
from pydantic import BaseModel

class NodeSource(BaseModel):
    path: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    isbn: Optional[str] = None

class NodeData(BaseModel):
    title: Optional[str] = None
    source: NodeSource | None = None  
