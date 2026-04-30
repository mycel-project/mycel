from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field

class NodeCreateFromUrl(BaseModel):
    type: Literal["url"]
    url: str

class NodeCreateFromText(BaseModel):  # placeholder
    type: Literal["text"]
    content: str

NodeCreate = Annotated[
    Union[NodeCreateFromUrl, NodeCreateFromText],
    Field(discriminator="type")
]
