from typing import Optional, Union
from src.models.node import Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.type_data import TypeData
from src.services.node_service import NodeService
from src.services.priority_service import PriorityService
from src.types.node_type import NodeType


class CreateNodeUseCase:
    def __init__(self, node_service: NodeService, priority_service: PriorityService):
        self._node_service = node_service
        self._priority_service = priority_service

    def execute(
        self,
        collection_id: int,
        type: NodeType,
        content: Union[str, dict, NodeContent],
        data: Optional[NodeData] = None,
        type_data: Optional[TypeData] = None,
        parent_id: Optional[int] = None,
        position: Optional[str] = None,
    ) -> Node:
        if position is None:
            if parent_id is None:
                position = self._priority_service.prioritise_random_between_percentage(collection_id, 5, 15)
            else:
                position = self._priority_service.prioritise_random_near_node(collection_id, parent_id, 10)

        return self._node_service.create_node(
            collection_id=collection_id,
            type=type,
            content=content,
            position=position,
            data=data,
            type_data=type_data,
            parent_id=parent_id,
        )
