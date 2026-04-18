from pydantic import BaseModel, Field
import json


class NodeContent(BaseModel):
    fields: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_input(cls, data):
        if data is None:
            return cls()

        if isinstance(data, NodeContent):
            return data

        if isinstance(data, str):
            return cls(fields={"0": data})

        if isinstance(data, dict):
            return cls(fields=data)

        raise ValueError("Invalid content format")

    @classmethod
    def from_db(cls, data):
        if not data:
            return cls()

        if isinstance(data, str):
            data = json.loads(data)

        return cls(fields=data)

    def to_db(self) -> str:
        return json.dumps(self.fields)
