from pydantic import BaseModel, ConfigDict

from src.models.user_conf import UserConf


class UserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    conf: UserConf
