from src.models.node import Node
from src.schemas.node_view import NodeView
from src.services.node_service import NodeService
from src.services.priority_service import PriorityService


class NodeViewBuilder:
    def __init__(self, node_service: NodeService, priority_service: PriorityService):
        self._node_service = node_service
        self._priority_service = priority_service

    def to_view(self, node: Node) -> NodeView:
        priority = self._priority_service.get_priority(node.collection_id, node.id)
        return self._node_service.node_to_view(node, priority)

    def to_views(self, nodes: list[Node]) -> list[NodeView]:
        return [self.to_view(n) for n in nodes]
