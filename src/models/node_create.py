from typing import Literal, Annotated, Union, Optional
from pydantic import BaseModel, Field

from src.models.node_data import NodeSource

class NodeCreateFromUrl(BaseModel):
    """
    Create a node by fetching content and data from a URL.

    The fetched content is converted to Markdown. Reach out if you need support for additional formats.
    """
    type: Literal["url"]
    url: str
    target_format: str = "markdown"
    tz_offset: int = 0

class NodeCreateFromText(BaseModel): 
    """
    Create a node from raw text content.
    """
    type: Literal["text"]
    content: str
    title: Optional[str] = None
    source: Optional[NodeSource] = Field(default=None, description="The source of the content, such as a file path or URL.")
    target_format: str = "markdown"
    inital_format: Optional[str] = None
    tz_offset: int = 0

NodeCreate = Annotated[
    Union[NodeCreateFromUrl, NodeCreateFromText],
    Field(discriminator="type")
]
