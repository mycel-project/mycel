from pydantic import BaseModel

from src.models.node import NodeType


class ReviewContext(BaseModel):
    """
    Review data used by scheduling engine
    """
    id: str
    learning_unit_type: NodeType
