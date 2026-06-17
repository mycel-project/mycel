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
        priorities = []
        for unit in node.learning_units:
            priorities.append(self._priority_service.position_to_priority(node.collection_id, unit.position))
        preview = node.fields.get_preview() or "No preview for this node"
        return self._node_service.node_to_view(node, priorities, preview)

    def to_detail_view(self, node: Node) -> NodeDetailView:
        view = self.to_view(node)
        learning_units_data = []
        for unit in node.learning_units:
            unit_dict = unit.model_dump()
            unit_dict["priority"] = self._priority_service.position_to_priority(node.collection_id, unit.position)
            learning_units_data.append(unit_dict)
        return NodeDetailView(
            **view.model_dump(),
            fields=node.fields,
            learning_units=learning_units_data,
            data=node.data,
        )

    def to_detail_views(self, nodes: list[Node]) -> list[NodeDetailView]:
        return [self.to_detail_view(n) for n in nodes]

    def to_views(self, nodes: list[Node]) -> list[NodeView]:
        return [self.to_view(n) for n in nodes]
