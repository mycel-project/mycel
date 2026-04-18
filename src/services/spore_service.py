from typing import Optional, Union

from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService
from src.types.node_type import NodeType


class SporeService:
    def __init__(self, node_service: NodeService, node_format_service: NodeFormatService):
        self._node_service = node_service
        self._node_format_service = node_format_service

    def create_spore(self, col_id: int, content: Union[str, dict], parent_id: Optional[int]):
        self._node_service.create_node(
            collection_id=col_id,
            content=content,
            parent_id=parent_id,
            type=NodeType.SPORE
        )
