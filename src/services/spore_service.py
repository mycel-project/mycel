from typing import Optional, Union

from src.schemas.node_update import NodeUpdate
from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService
from src.types.node_type import NodeType
from src.models.node import Node


class SporeService:
    def __init__(self, node_service: NodeService, node_format_service: NodeFormatService):
        self._node_service = node_service
        self._node_format_service = node_format_service

    def create_spore(self, col_id: int, content: Union[str, dict], parent_id: Optional[int]) -> Node:
        return self._node_service.create_node(
            collection_id=col_id,
            content=content,
            parent_id=parent_id,
            type=NodeType.SPORE
        )

    def cloze_region(self, node_id: int, text: str, field: str, start: int, end: int) -> Node:
        node = self._node_service.get_node(node_id)
        if not node:
            raise ValueError(f"No node found for id {node_id}")
        self._node_format_service.cloze_region(node, field, start, end, text)
        self._node_service.update(
            node_id,
            NodeUpdate(content=node.content)
        )
        return node

    def remove_extract_formatting(self, node_id: int, field_key: str = "0") -> Node:
        node = self._node_service.get_node(node_id)
        if not node:
            raise ValueError(f"No node found for id {node_id}")
        field_content = node.content.fields[field_key]
        
        text_without_inline = self._node_format_service.remove_inline_code_formatting(field_content)
        fully_cleaned_text = self._node_format_service.remove_blockquote_formatting(text_without_inline, r"\{\{c\d+::\s*")

        node.content.fields[field_key] = fully_cleaned_text
        self._node_service.update(
            node.id,
            NodeUpdate(content=node.content)
        )
        
        return node
