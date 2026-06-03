from typing import Optional
from pydantic import BaseModel, model_validator

from src.models.user_conf import UserConf


class UserUpdate(BaseModel):
    """
    Partial update model for User.
    
    Only include fields that you explicitly want to modify.
    Any field provided in this model including fields set to None will be applied and will overwrite the existing value on the user.

    Fields not included in the update will remain unchanged.
    """
    name: Optional[str] = None
    conf: Optional[UserConf] = None
