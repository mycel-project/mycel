from typing import Optional
import json

from pydantic import BaseModel, field_validator

class NodeUpdate(BaseModel):
    parent_id: Optional[int] = None
    content: Optional[dict] = None
    type: Optional[int] = None
    due: Optional[int] = None
    priority: Optional[str] = None    
    state: Optional[int] = None
    last_review: Optional[int] = None
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    step: Optional[int] = None

    @field_validator("type", "state", "step")
    def validate_int_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("Must be positive")
        return v

    @field_validator("stability", "difficulty")
    def validate_float_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("Must be positive")
        return v

    @field_validator("content", mode="before") 
    def parse_content(cls, v):
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {"value": v}
        return v

    class Config:
        exclude_none = True
