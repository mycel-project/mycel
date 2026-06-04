import json
from pydantic import BaseModel, ConfigDict

from src.models.user_conf import UserConf


class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: str
    name: str
    created_at: int
    conf: UserConf
        
    @classmethod
    def from_db(cls, row: dict) -> 'User':
        row_dict = dict(row) if hasattr(row, 'keys') else row.__dict__

        raw_conf = row_dict["conf"]
        parsed_conf = json.loads(raw_conf) if isinstance(raw_conf, str) else raw_conf

        return cls(
            id=row_dict["id"],
            name=row_dict["name"],
            created_at=row_dict["created_at"],
            conf=UserConf.model_validate(parsed_conf)
        )
