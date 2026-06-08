from typing import Annotated, Literal
from pydantic import BaseModel, Field
from src.models.base_learning_unit import BaseLearningUnit

class FsrsData(BaseModel):
    type: Literal["fsrs"] = "fsrs"
    state: int = 1
    stability: float
    difficulty: float
    step: int

class PlaceholderData(BaseModel):
    """
    Placeholder class to allow discriminator in Spore model
    """
    type: Literal["placeholder"] = "placeholder" 

LearningData = Annotated[FsrsData | PlaceholderData, Field(discriminator="type")]

class Spore(BaseLearningUnit):
    type: Literal["spore"] = "spore"
    ord: int
    learning_data: LearningData
