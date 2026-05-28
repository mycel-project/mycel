from typing import Optional, Union
from src.core.scheduling_engine import SchedulingEngine
from src.domain.create_node_usecase import CreateNodeUseCase
from src.models.node import Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.type_data import TypeData
from src.services.node_service import NodeService
from typing import Optional

from src.types.node_type import NodeType
from src.utils.time import MS_PER_DAY, now_ms, start_of_local_day_ms


class CreateFragmentUseCase:
    def __init__(self, node_service: NodeService, scheduling_engine: SchedulingEngine, create_node_use_case: CreateNodeUseCase):
        self._node_service = node_service
        self._scheduling_engine = scheduling_engine
        self._create_node = create_node_use_case

    def execute(
        self,
        collection_id: int,
        content: Union[str, dict, NodeContent],
        data: Optional[NodeData] = None,
        type_data: Optional[TypeData] = None,
        parent_id: Optional[int] = None,
        tz_offset: int = 0,
        due: int | None = None,
    ) -> Node:

        if parent_id != None:
            parent_depth = self._node_service.get_depth(parent_id)
            depth = parent_depth + 1
        else:
            depth = 0

        if due is None:
            interval = self._scheduling_engine.compute_fragment_next_interval(depth, 0)
            due = start_of_local_day_ms(now_ms() + interval * MS_PER_DAY, tz_offset)
            
        return self._create_node.execute(
            collection_id=collection_id,
            type=NodeType.FRAGMENT,
            content=content,
            data=data,
            due=due,
            type_data=type_data,
            parent_id=parent_id,
        )
