from typing import Literal, Optional
from pydantic import BaseModel, field_validator

class NodeSource(BaseModel):
    path: Optional[str] = None
    url: Optional[str] = None
    md5: Optional[str] = None
    isbn: Optional[str] = None

class NodeData(BaseModel):
    title: Optional[str] = None
    content_format: str = "markdown" # Create dedicated index in sql if it is slow
    source: NodeSource | None = None

    @field_validator("content_format")
    @classmethod
    def normalize_format(cls, v: str) -> str:
        return v.strip().lower()
