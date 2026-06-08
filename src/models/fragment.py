from typing import Literal, Annotated
from pydantic import BaseModel, Field
from src.models.base_learning_unit import BaseLearningUnit

class EbookRef(BaseModel):
    type: Literal["ebook"] = "ebook" 
    anchor_start: str
    anchor_end: str | None = None
    margin_before: int = 0
    margin_after: int = 0

class VideoRef(BaseModel):
    type: Literal["video"] = "video"
    timestamp_start: int | None = None
    timestamp_end: int | None = None

FragmentRef = Annotated[EbookRef | VideoRef, Field(discriminator="type")]

class Fragment(BaseLearningUnit):
    type: Literal["fragment"] = "fragment" 
    dismiss: bool = False
    ref: FragmentRef | None = None

