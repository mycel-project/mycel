from typing import Optional
from src.models.node_content import NodeContent
from src.schemas.node_view import NodeView


class NodeDetailView(NodeView):
    """Full view for single node with all content."""
    content: Optional[NodeContent]
