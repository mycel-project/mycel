from typing import Optional, Literal
from pydantic import field_validator

from src.models.type_review_data.base_type_review_data import BaseTypeReviewData


class SporeReviewData(BaseTypeReviewData):
    rating: int

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v is not None and v < 0:
            raise ValueError("Must be positive")
        return v
