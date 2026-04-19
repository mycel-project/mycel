from typing import Optional, Union

from _pytest.nodes import NodeMeta
from src.models.node import Node
from src.schemas.node_update import NodeUpdate
from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService
from src.types.node_type import NodeType


class FragmentService:
    def __init__(self, node_service: NodeService, node_format_service: NodeFormatService):
        self._node_service = node_service
        self._node_format_service = node_format_service
        self._emphasis_handlers = {
            NodeType.FRAGMENT: self._node_format_service.blockquote_region,
            NodeType.SPORE: self._node_format_service.inline_region,
        }

        
    def create_fragment(self, col_id: int, content: Union[str, dict], parent_id: Optional[int] = None):
        self._node_service.create_node(
            collection_id=col_id,
            content=content,
            parent_id=parent_id,
            type=NodeType.FRAGMENT
        )

        
    def emphasize_region(self, node_id: int, node_region_type: int, text: str, field: str, start: int, end: int):
        node = self._node_service.get_node(node_id)
        if not node:
            raise ValueError(f"No node found for id {node_id}")

        handler = self._emphasis_handlers.get(NodeType(node_region_type))
        if not handler:
            raise ValueError("Unsupported type")

        node = handler(node, field, start, end, text)

        self._node_service.update(
            node_id,
            NodeUpdate(content=node.content)
        )
