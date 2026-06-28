from typing import Optional
from src.core.scheduling_engine import SchedulingEngine
from src.domain.create_node_usecase import CreateNodeUseCase
from src.models.node import Node, NodeFields, NodeStatus, NodeType
from src.models.node_data import NodeData
from src.models.spore import Spore
from src.models.template import DefaultTemplate
from src.services.node_service import NodeService
from typing import Optional

from src.utils.time import start_of_local_tomorrow_ms


class CreateSporeUseCase:
    def __init__(self, node_service: NodeService, scheduling_engine: SchedulingEngine, create_node_use_case: CreateNodeUseCase):
        self._node_service = node_service
        self._scheduling_engine = scheduling_engine
        self._create_node = create_node_use_case

    def execute(
        self,
        user_id: str,
        collection_id: str,
        fields: NodeFields,
        status: NodeStatus = NodeStatus.ACTIVE,
        template_id: DefaultTemplate = DefaultTemplate.SPORE_CLOZE,
        data: Optional[NodeData] = None,
        parent_id: Optional[str] = None,
        tz_offset: int = 0,
        due: int | None = None,
        position: Optional[str] = None,
    ) -> Node:

        due = start_of_local_tomorrow_ms(tz_offset)

        spore_unit = Spore(due=due, slot=1)
        return self._create_node.execute(
            user_id=user_id,
            collection_id=collection_id,
            template_id=template_id,
            type=NodeType.SPORE,
            learning_unit=spore_unit,
            fields=fields,
            data=data,
            status=status,
            parent_id=parent_id,
            position=position,
        )
