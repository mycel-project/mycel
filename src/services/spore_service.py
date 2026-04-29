from typing import Optional, Union

from src.core.cloze import CLOZE_PATTERN
from src.domain.domain_exceptions import ClozeValidationError, InvalidNodeUpdate, NotASpore
from src.models.node_content import NodeContent
from src.schemas.node_update import NodeUpdate
from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService
from src.types.node_type import NodeType
from src.models.node import Node

class SporeService:
    def __init__(self, node_service: NodeService, node_format_service: NodeFormatService):
        self._node_service = node_service
        self._node_format_service = node_format_service

    def create_spore(self, col_id: int, content: Union[str, dict], parent_id: Optional[int] = None) -> Node:
        return self._node_service.create_node(
            collection_id=col_id,
            content=content,
            parent_id=parent_id,
            type=NodeType.SPORE
        )

    def update_spore(self, node_id: int, data: NodeUpdate) -> Node:
        node = self._node_service.get_node(node_id)
        if node.type != NodeType.SPORE:
            raise NotASpore(node_id)
        content = data.content
        if content is not None:
            try:
                self.validate_spore_content(content)
            except ValueError as e:
                raise InvalidNodeUpdate(node_id, node.type, content, str(e)) from ClozeValidationError(str(content))
        return self._node_service.update(node_id, data)

    def validate_spore_content(self, content: NodeContent):
        field = content.get_first_field()

        if field is None:
            raise ValueError("Content is empty")

        if not self.has_cloze(field):
            raise ValueError("No cloze regex detected")

    def has_cloze(self, content: str) -> bool:
        return CLOZE_PATTERN.search(content) is not None

    def cloze_region(self, node_id: int, text: str, field: str, start: int, end: int) -> Node:
        node = self._node_service.get_node(node_id)

        clozed_node = self._node_format_service.cloze_region(node, field, start, end, text)
        content = clozed_node.content.fields[field]
        if not self.has_cloze(content):
            raise ClozeValidationError(content)
        return self._node_service.update(
            node_id,
            NodeUpdate(content=node.content)
        )

    def remove_extract_formatting(self, node_id: int, field_key: str = "0") -> Node:
        node = self._node_service.get_node(node_id)

        field_content = node.content.fields[field_key]
        
        text_without_inline = self._node_format_service.remove_inline_code_formatting(field_content)
        fully_cleaned_text = self._node_format_service.remove_blockquote_formatting(text_without_inline, r"\{\{c\d+::\s*")

        node.content.fields[field_key] = fully_cleaned_text
        self._node_service.update(
            node.id,
            NodeUpdate(content=node.content)
        )
        
        return node
