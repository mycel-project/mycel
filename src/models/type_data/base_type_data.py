from pydantic import BaseModel
import json

class BaseTypeData(BaseModel):
    pass


    @classmethod
    def from_db(cls, data):
        if not data:
            return cls()

        if isinstance(data, str):
            data = json.loads(data)

        return cls(fields=data)
