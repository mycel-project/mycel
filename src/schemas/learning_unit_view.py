from typing import Annotated
from pydantic import Field, TypeAdapter
from src.models.fragment import Fragment
from src.models.spore import Spore

class SporeView(Spore):
    priority: float
    position: str = Field(default="", exclude=True)  

class FragmentView(Fragment):
    priority: float
    position: str = Field(default="", exclude=True) 

LearningUnitView = Annotated[FragmentView | SporeView, Field(discriminator="type")]
learning_unit_view_adapter = TypeAdapter(LearningUnitView)
