from pydantic import BaseModel
from typing import Optional

class NodeData(BaseModel):
    title: Optional[str] = None
    src: Optional[str] = None

    def to_db(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_db(cls, data):
        if not data:
            return cls()
        if isinstance(data, str):
            return cls.model_validate_json(data)
        return cls.model_validate(data)
