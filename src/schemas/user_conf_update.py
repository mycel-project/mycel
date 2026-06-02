from typing import Optional
from pydantic import BaseModel, model_validator


class UserConfUpdate(BaseModel):
    undo_review_max_age: Optional[int] = None
    delete_max_age: Optional[int] = None
    ping_frequency: Optional[int] = None
    add_extract_to_nav: Optional[bool] = None
    wait_for_due_time: Optional[bool] = None
    # test_param: Optional[str] = None
    # test_bool: Optional[bool] = None
