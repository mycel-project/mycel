from typing import Optional
from pydantic import BaseModel, model_validator

from src.models.user_conf import UserConf

class UserUpdate(BaseModel):
    name: Optional[str] = None
    conf: Optional[UserConf] = None
