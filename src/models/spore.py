from typing import Annotated, Literal
from fractional_indexing import Optional
from pydantic import BaseModel, Field
from src.models.base_learning_unit import BaseLearningUnit

class FsrsData(BaseModel):
    type: Literal["fsrs"] = "fsrs"
    state: int = 1
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    step: Optional[int] = None

class PlaceholderData(BaseModel):
    """
    Placeholder class to allow discriminator in Spore model
    """
    type: Literal["placeholder"] = "placeholder" 

LearningData = Annotated[FsrsData | PlaceholderData, Field(discriminator="type")]

class Spore(BaseLearningUnit):
    type: Literal["spore"] = "spore"
    learning_data: LearningData = Field(default_factory=FsrsData)

    def get_fsrs_data(self) -> FsrsData:
        if not isinstance(self.learning_data, FsrsData):
            raise RuntimeError("Spore has no FSRS data yet")
        return self.learning_data
