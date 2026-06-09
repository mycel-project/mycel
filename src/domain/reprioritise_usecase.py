from src.models.node import Node
from src.services.node_service import NodeService
from src.services.priority_service import PriorityService


class ReprioritiseUseCase:
    def __init__(
        self,
        node_service: NodeService,
        priority_service: PriorityService, 
    ):
        self._node_service = node_service
        self._priority_service = priority_service

    def execute(self, col_id: str, node_id: str, slot: int, target_node_priority: float) -> Node:
        node = self._node_service.get_node(node_id)
        learning_unit = node.get_unit_by_slot(slot)
        self._priority_service.reprioritise_node(col_id, learning_unit.id, target_node_priority)
        return self._node_service.get_node_from_learning_unit(learning_unit.id)
