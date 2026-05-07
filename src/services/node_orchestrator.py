from typing import Union, Optional
import logging

from src.domain.domain_exceptions import ExtractError, ExtractMismatchError, InvalidSourceNodeType, NotAKnownType, UnknownRessourceTypeError
from src.models.extract_result import ExtractResult
from src.models.node import Node
from src.models.node_create import NodeCreate, NodeCreateFromUrl
from src.schemas.node_update import NodeUpdate
from src.schemas.node_view import NodeView
from src.services.fragment_service import FragmentService
from src.services.node_service import NodeService
from src.services.spore_service import SporeService
from src.types.node_type import NodeType


logger = logging.getLogger(__name__)

class NodeOrchestrator:
    # Only CRUD orchestration ? 
    def __init__(self, node_service: NodeService, fragment_service: FragmentService, spore_service: SporeService):
        self._node_service = node_service
        self._fragment_service = fragment_service
        self._spore_service = spore_service

    def create_node_to_view(self, collection_id: int, data: NodeCreate) -> NodeView:
        new_node = self.create_node(collection_id, data)
        position = self._node_service.get_position(new_node.collection_id, new_node.id)
        return self._node_service.node_to_view(new_node, position)

    def create_node(self, collection_id: int, data: NodeCreate) -> Node:
        if isinstance(data, NodeCreateFromUrl):
            return self._node_service.create_node_from_url(collection_id, data.url)
        else:
            raise UnknownRessourceTypeError(type(data).__name__)

    def update_node_to_view(self, node_id: int, data: NodeUpdate) -> NodeView:
        updated_node = self.update_node(node_id, data)
        position = self._node_service.get_position(updated_node.collection_id, updated_node.id)
        return self._node_service.node_to_view(updated_node, position)

    def update_node(self, node_id, data: NodeUpdate) -> Node:
        """
        Higher level dispatching than node_service.update() to allow specific verifications based on node type
        """
        node = self._node_service.get_node(node_id)
        if node.type == NodeType.FRAGMENT:
            return self._fragment_service.update_fragment(node_id, data)
        elif node.type == NodeType.SPORE:
            return self._spore_service.update_spore(node_id, data)
        else:
            raise NotAKnownType(node_id, node.type)

    def create_extract(self, col_id: int, extract_type: int, source_node_id: int, text: str, field: int, start_index: int, end_index: int) -> ExtractResult:
        source_node = self._node_service.get_node(source_node_id)
        rebuilt_text = source_node.content.fields[str(field)][start_index:end_index]
        
        if rebuilt_text != text: # We compare to avoid incoherences
            raise ExtractMismatchError(rebuilt_text, text)
        if "\n" in text and extract_type == NodeType.SPORE: # I forgot why
            raise ExtractError("EXTRACT_ERROR", "Spore can't include new lines")            
        if source_node.type != NodeType.FRAGMENT:
            raise InvalidSourceNodeType(source_node_id, extract_type)
        
        if extract_type == NodeType.FRAGMENT:
            extract = self._fragment_service.create_fragment(col_id, text, source_node_id)
        elif extract_type == NodeType.SPORE:
            source_content = next(iter(source_node.content.fields.values())) # temp, need simplification
            spore = self._spore_service.create_spore(col_id, source_content, source_node_id)
            try: 
                clozed_spore = self._spore_service.cloze_region(spore.id, text, str(field), start_index, end_index)
                extract = self._spore_service.remove_extract_formatting(clozed_spore.id, str(field))
            except Exception:
                self._node_service.delete_node(spore.id)
                raise
        else:
            raise NotAKnownType(source_node_id, extract_type)
        
        source = source_node
        try:
            source = self._fragment_service.emphasize_region(source_node_id, extract_type, text, str(field), start_index, end_index)
        except Exception as e:
            logger.warning(f"Failed to emphasize region in parent (id {source_node_id}), but extract is valid: {e}")
        
        return ExtractResult(
            extract_node=extract,
            source_node=source
        )
