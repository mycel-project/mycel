from pydantic import BaseModel

from src.models.node import Node
from src.schemas.node_view import NodeView

class ExtractResult(BaseModel):
    # result to send to front
    extract_node: NodeView
    source_node: NodeView

