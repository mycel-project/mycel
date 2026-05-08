from pydantic import BaseModel, model_validator

from src.models.user_conf import UserConf


class User(BaseModel):
    id: int
    name: str
    created_at: int
    conf: UserConf
        
