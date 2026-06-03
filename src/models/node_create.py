from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field

class NodeCreateFromUrl(BaseModel):
    type: Literal["url"]
    url: str
    tz_offset: int = 0

class NodeCreateFromText(BaseModel):  # placeholder
    type: Literal["text"]
    content: str
    tz_offset: int = 0

NodeCreate = Annotated[
    Union[NodeCreateFromUrl, NodeCreateFromText],
    Field(discriminator="type")
]
