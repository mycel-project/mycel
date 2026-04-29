from pydantic import BaseModel

from src.models.node import Node

class ExtractResult(BaseModel):
    extract_node: Node
    source_node: Node

