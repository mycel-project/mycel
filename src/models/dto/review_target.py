from pydantic.main import BaseModel

from src.schemas.node_detail_view import NodeDetailView


class ReviewTarget(BaseModel):
    node: NodeDetailView
    slot: int = 1
