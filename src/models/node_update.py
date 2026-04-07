from pydantic import BaseModel, validator
from typing import Optional
import json


class NodeUpdate(BaseModel):
    content: Optional[dict] = None
    type: Optional[int] = None
    state: Optional[int] = None
    due: Optional[int] = None
    priority: Optional[str] = None

    @validator("type", "state")
    def validate_int_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("Must be positive")
        return v

    @validator("content", pre=True)
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
