from pydantic import BaseModel

from src.schemas.node_detail_view import NodeDetailView

class ExtractResult(BaseModel):
    # result to send to front
    extract_node: NodeDetailView
    source_node: NodeDetailView

