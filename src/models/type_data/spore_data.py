from typing import Optional, Literal
from pydantic import field_validator

from src.models.type_data.base_type_data import BaseTypeData


class SporeData(BaseTypeData):
    state: int = 1
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    step: Optional[int] = None

    @field_validator("stability", "difficulty")
    @classmethod
    def validate_float_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("Must be positive")
        return v

    @field_validator("state", "step")
    @classmethod
    def validate_int_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("Must be positive")
        return v
