from typing import Optional
from pydantic import BaseModel, model_validator


class UserConfUpdate(BaseModel):
    undo_review_max_age: Optional[int] = None
    delete_max_age: Optional[int] = None
    ping_frequency: Optional[int] = None
    # test_param: Optional[str] = None
    # test_bool: Optional[bool] = None
