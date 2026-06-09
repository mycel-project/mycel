from typing import Optional
from src.models.learning_unit import LearningUnit
from src.models.node import Node, NodeFields, NodeStatus, NodeType
from src.models.node_data import NodeData
from src.services.node_service import NodeService
from src.services.priority_service import PriorityService
from typing import Optional

class CreateNodeUseCase:
    def __init__(self, node_service: NodeService, priority_service: PriorityService):
        self._node_service = node_service
        self._priority_service = priority_service

    def execute(
        self,
        user_id: str,
        collection_id: str,
        template_id: str,
        type: NodeType,
        fields: NodeFields,
        learning_unit: LearningUnit,
        position: Optional[str] = None,
        data: Optional[NodeData] = None,
        status: NodeStatus = NodeStatus.ACTIVE,
        parent_id: Optional[str] = None
    ) -> Node:
        if position is None:
            if parent_id is None:
                position = self._priority_service.prioritise_random_between_percentage(collection_id, 85, 95)
            else:
                parent = self._node_service.get_node(parent_id)
                parent_priority = self._priority_service.position_to_priority(collection_id, parent.get_fragment().position)
                position = self._priority_service.prioritise_random_near_priority(collection_id, parent_priority, 10)

        learning_unit.position = position

        return self._node_service.create_node(
            user_id=user_id,
            collection_id=collection_id,
            template_id=template_id,
            type=type,
            fields=fields,
            learning_unit=learning_unit,
            data=data,
            status=status,
            parent_id=parent_id,
        )
