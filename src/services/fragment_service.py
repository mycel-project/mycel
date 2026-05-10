from typing import Optional, Union

from _pytest.nodes import NodeMeta
from src.domain.create_node_usecase import CreateNodeUseCase
from src.domain.domain_exceptions import NotAFragment, NotAKnownType
from src.models.node import Node
from src.schemas.node_update import NodeUpdate
from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService
from src.types.node_type import NodeType


class FragmentService:
    def __init__(
        self,
        node_service: NodeService,
        node_format_service: NodeFormatService,
        create_node_use_case: CreateNodeUseCase,
    ):
        self._node_service = node_service
        self._node_format_service = node_format_service
        self._create_node = create_node_use_case
        self._emphasis_handlers = {
            NodeType.FRAGMENT: self._node_format_service.blockquote_region,
            NodeType.SPORE: self._node_format_service.inline_region,
        }
        
    def create_fragment(self, col_id: int, content: Union[str, dict], parent_id: Optional[int] = None) -> Node:
        return self._create_node.execute(
            collection_id=col_id,
            content=content,
            parent_id=parent_id,
            type=NodeType.FRAGMENT
        )

    def update_fragment(self, node_id: int, data: NodeUpdate) -> Node:
        node = self._node_service.get_node(node_id)
        if node.type != NodeType.FRAGMENT:
            raise NotAFragment(node_id)
        return self._node_service.update(node_id, data)
        
    def emphasize_region(self, node_id: int, node_region_type: int, text: str, field: str, start: int, end: int) -> Node:
        node = self._node_service.get_node(node_id)

        handler = self._emphasis_handlers.get(NodeType(node_region_type))
        if not handler:
            raise NotAKnownType(node_id, node_region_type)

        node = handler(node, field, start, end, text)

        return self._node_service.update(
            node_id,
            NodeUpdate(content=node.content)
        )

        
