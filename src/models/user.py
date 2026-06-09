import json

from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.template import Templates
from src.models.user_conf import UserConf
from src.utils.time import now_ms


class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    created_at: int = Field(default_factory=lambda: now_ms())
    conf: UserConf = Field(default_factory=UserConf)
    templates: Templates = Field(default_factory=Templates)

    @field_validator("conf", "templates", mode="before")
    @classmethod
    def deserialize_json_strings(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
