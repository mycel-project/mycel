from pydantic import BaseModel, model_validator


class UserConf(BaseModel):
    undo_review_max_age: int = 300
    ping_frequency: int = 3
