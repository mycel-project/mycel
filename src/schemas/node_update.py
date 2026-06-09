from typing import Optional

from pydantic import BaseModel, field_validator

from src.models.node import NodeFields, NodeStatus
from src.models.node_data import NodeData

class NodeUpdate(BaseModel):
    """
    Partial update model for Node.

    Only include fields that you explicitly want to modify.
    Any field provided in this model including fields set to None will be applied and will overwrite the existing value on the node.

    Fields not included in the update will remain unchanged.
    """
    parent_id: Optional[str] = None
    fields: Optional[NodeFields] = None
    data: Optional[NodeData] = None
    status: Optional[NodeStatus] = None
    deleted_at: Optional[int] = None
    updated_at: Optional[int] = None
