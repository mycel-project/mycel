from typing import Union, Optional

from src.services.fragment_service import FragmentService
from src.services.node_service import NodeService
from src.services.spore_service import SporeService
from src.types.node_type import NodeType


class NodeOrchestrator:
    def __init__(self, node_service: NodeService, fragment_service: FragmentService, spore_service: SporeService):
        self._node_service = node_service
        self._fragment_service = fragment_service
        self._spore_service = spore_service

    def create_node_dispatch(self, col_id: int, type: int, content: str | dict):
        if type == NodeType.FRAGMENT:
            self._fragment_service.create_fragment(col_id, content)
        elif type == NodeType.SPORE:
            self._spore_service.create_spore(col_id, content)
        else:
            raise ValueError(f"Node type with index {type} does not exist, can't create node.")

    def create_extract(self, col_id: int, type: int, source_node_id: int, text: str, field: int, start_index: int, end_index: int):
        source_node = self._node_service.get_node(source_node_id)
        
        if not source_node:
            raise ValueError(f"No node found for id {source_node_id}, can't create extract")
        rebuilt_text = source_node.content.fields[str(field)][start_index:end_index]
        if rebuilt_text != text: # We compare to avoid incoherences
            raise ValueError(
                "Selection mismatch: extracted content differs from reconstructed slice. "
                "Possible sync or encoding issue."
            )
        if "\n" in text and type == NodeType.SPORE:
            raise ValueError("Spore can't include new lines")            
        if source_node.type != NodeType.FRAGMENT:
            raise ValueError("You can only create a new node from a fragment")

        if type == NodeType.FRAGMENT:
            self._fragment_service.create_fragment(col_id, text, source_node_id)
        elif type == NodeType.SPORE:
            source_content = next(iter(source_node.content.fields.values())) # need simplification
            spore = self._spore_service.create_spore(col_id, source_content, source_node_id)
            clozed_spore = self._spore_service.cloze_region(spore.id, text, str(field), start_index, end_index)
            self._spore_service.remove_extract_formatting(clozed_spore.id, str(field))

            
        self._fragment_service.emphasize_region(source_node_id, type, text, str(field), start_index, end_index)
