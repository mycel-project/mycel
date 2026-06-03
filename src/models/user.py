from pydantic import BaseModel, ConfigDict

from src.models.user_conf import UserConf


class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: str
    name: str
    created_at: int
    conf: UserConf
        
