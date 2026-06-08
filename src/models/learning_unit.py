from typing import Annotated

from pydantic import Field

from src.models.fragment import Fragment
from src.models.spore import Spore


LearningUnit = Annotated[Fragment | Spore, Field(discriminator="type")]
