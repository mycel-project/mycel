import time
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

from src.models.template import Templates
from src.models.user_conf import UserConf


class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    conf: UserConf = Field(default_factory=UserConf)
    templates: Templates = Field(default_factory=Templates)

