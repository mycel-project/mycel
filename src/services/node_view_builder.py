from src.models.node import Node
from src.schemas.node_detail_view import NodeDetailView
from src.schemas.node_view import NodeView
from src.services.node_service import NodeService
from src.services.priority_service import PriorityService


class NodeViewBuilder:
    def __init__(self, node_service: NodeService, priority_service: PriorityService):
        self._node_service = node_service
        self._priority_service = priority_service

    def to_view(self, node: Node) -> NodeView:
        priority = self._priority_service.get_priority(node.collection_id, node.id)
        preview = node.content.get_first_field() if node.content else None
        content_preview = preview[:150] if preview else None
        assert content_preview != None
        return self._node_service.node_to_view(node, priority, content_preview)

    def to_detail_view(self, node: Node) -> NodeDetailView:
        view = self.to_view(node)
        return NodeDetailView(
            **view.model_dump(),
            content=node.content,
        )

    def to_views(self, nodes: list[Node]) -> list[NodeView]:
        return [self.to_view(n) for n in nodes]
