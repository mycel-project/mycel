from src.models.node import NodeFields
from src.schemas.node_view import NodeView


class NodeDetailView(NodeView):
    """Full view for single node with all content."""
    fields: NodeFields 
