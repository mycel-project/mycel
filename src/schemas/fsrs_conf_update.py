from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Tuple


class FsrsConfUpdate(BaseModel):
    parameters: Optional[Tuple[float, ...]] = None
    desired_retention: Optional[float] = None
    learning_steps: Optional[Tuple[int, ...]] = None
    relearning_steps: Optional[Tuple[int, ...]] = None
    maximum_interval: Optional[int] = None
    enable_fuzzing: Optional[bool] = None

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("learning_steps", "relearning_steps", mode="before")
    @classmethod
    def parse_steps(cls, v):
        if v is None:
            return v

        if isinstance(v, str):
            return tuple(int(x.strip()) for x in v.split(","))

        if isinstance(v, list):
            return tuple(v)

        return v
