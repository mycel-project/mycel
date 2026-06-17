from typing import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field, TypeAdapter

from src.models.fragment import FragmentRef
from src.models.spore import LearningData


class BaseLearningUnitUpdate(BaseModel):
    due: Optional[int] = None
    position: Optional[str] = None
    last_review: Optional[int] = None

class FragmentUpdate(BaseLearningUnitUpdate):
    type: Literal["fragment"] = "fragment"
    dismiss: Optional[bool] = None
    ref: Optional[FragmentRef] = None

class SporeUpdate(BaseLearningUnitUpdate):
    type: Literal["spore"] = "spore"
    learning_data: Optional[LearningData] = None

LearningUnitUpdate = Annotated[
    Union[FragmentUpdate, SporeUpdate],
    Field(discriminator="type")
]

lu_update_adapter = TypeAdapter(LearningUnitUpdate)
