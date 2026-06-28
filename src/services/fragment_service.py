from typing import Optional

from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.domain.domain_exceptions import NotAFragment, NotAKnownType
from src.models.node import Node, NodeFields, NodeType
from src.models.template import DefaultTemplate
from src.schemas.learning_unit_update import FragmentUpdate
from src.schemas.node_update import NodeUpdate
from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService


class FragmentService:
    def __init__(
        self,
        node_service: NodeService,
        node_format_service: NodeFormatService,
        create_fragment_use_case: CreateFragmentUseCase,
    ):
        self._node_service = node_service
        self._node_format_service = node_format_service
        self._create_fragment = create_fragment_use_case
        self._emphasis_handlers = {
            NodeType.FRAGMENT: self._node_format_service.blockquote_region,
            NodeType.SPORE: self._node_format_service.inline_region,
        }
        
    def create_fragment(self, user_id: str, col_id: str, content: str, parent_id: Optional[str] = None, tz_offset: int = 0) -> Node:
        return self._create_fragment.execute(
            user_id=user_id,
            collection_id=col_id,
            fields=NodeFields(root={"content": content}),
            template_id=DefaultTemplate.FRAGMENT_BASIC,
            parent_id=parent_id,
            tz_offset=tz_offset,
        )

    def update_fragment(self, node_id: str, data: NodeUpdate) -> Node:
        node = self._node_service.get_node(node_id)
        if node.base_for != NodeType.FRAGMENT:
            raise NotAFragment(node_id)
        return self._node_service.update(node_id, data)
        
    def emphasize_region(self, node_id: str, node_region_type: NodeType, field: str, start: int, end: int, text: str | None = None) -> Node:
        """
        Text is used to see if rebuild text is similar to what is passed in text (it should be)
        """
        node = self._node_service.get_node(node_id)

        handler = self._emphasis_handlers.get(NodeType(node_region_type))
        if not handler:
            raise NotAKnownType(node_id, node_region_type)

        node = handler(node, field, start, end, text)

        return self._node_service.update(
            node_id,
            NodeUpdate(fields=node.fields)
        )

    def dismiss(self, node_id: str, slot: int = 1, value: bool | None = None) -> Node:
        """
        Just first slot at the moment
        """
        node = self._node_service.get_node(node_id)
        fragment = node.get_fragment()
        if value is None:
            value = not fragment.dismiss
        return self._node_service.update_learning_unit(node_id, fragment.slot, FragmentUpdate(dismiss=value))
