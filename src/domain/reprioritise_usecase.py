from src.models.node import Node
from src.schemas.node_update import NodeUpdate
from src.services.node_service import NodeService
from src.services.priority_service import PriorityService
from src.utils.time import now_ms


class ReprioritiseUseCase:
    def __init__(
        self,
        node_service: NodeService,
        priority_service: PriorityService, 
    ):
        self._node_service = node_service
        self._priority_service = priority_service

    def execute(self, col_id: str, node_id: str, target_node_priority: float) -> Node:
        self._priority_service.reprioritise_node(col_id, node_id, target_node_priority)
#        return self._node_service.update(node_id, NodeUpdate(updated_at=now_ms())) # Not really interesting to set updated_at juste for reprioritise I guess
        return self._node_service.get_node(node_id)
