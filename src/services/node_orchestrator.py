import logging

from src.domain.create_node_from_url_usecase import CreateNodeFromUrlUseCase
from src.domain.domain_exceptions import EmptyField, ExtractError, ExtractMismatchError, InvalidSourceNodeType, NotAKnownType, UnknownRessourceTypeError
from src.domain.get_outline_usecase import GetOutlineUseCase
from src.domain.reschedule_node_usecase import RescheduleNodeUseCase
from src.domain.split_node_usecase import SplitNodeUseCase
from src.models.extract_result import ExtractResult
from src.models.node import Node
from src.models.node_create import NodeCreate, NodeCreateFromUrl
from src.models.outline import Outline
from src.schemas.node_update import NodeUpdate
from src.schemas.node_view import NodeView
from src.services.fragment_service import FragmentService
from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService
from src.services.node_view_builder import NodeViewBuilder
from src.services.spore_service import SporeService
from src.services.priority_service import PriorityService
from src.services.ressource_service import RessourceService
from src.types.node_type import NodeType
from src.utils.time import start_of_local_tomorrow_ms


logger = logging.getLogger(__name__)

class NodeOrchestrator:
    def __init__(self,
        node_service: NodeService,
        fragment_service: FragmentService,
        spore_service: SporeService,
        priority_service: PriorityService,
        ressource_service: RessourceService,
        node_view_builder: NodeViewBuilder,
        node_format_service: NodeFormatService,
        create_node_from_url_usecase: CreateNodeFromUrlUseCase,
        reschedule_node_usecase: RescheduleNodeUseCase,
        get_outline_usecase: GetOutlineUseCase,
        split_node_usecase: SplitNodeUseCase,
    ):
        self._node_service = node_service
        self._fragment_service = fragment_service
        self._spore_service = spore_service
        self._priority_service = priority_service
        self._ressource_service = ressource_service
        self._create_node_from_url_usecase = create_node_from_url_usecase
        self._node_view_builder = node_view_builder
        self._node_format_service = node_format_service
        self._reschedule_node_usecase = reschedule_node_usecase
        self._get_outline_usecase = get_outline_usecase
        self._split_node = split_node_usecase

    def _check_text_match(self, node: Node, field: int, start_index: int, end_index: int, text: str) -> None:
        rebuilt_text = node.content.fields[str(field)][start_index:end_index]
        if rebuilt_text != text:
            raise ExtractMismatchError(rebuilt_text, text)

    def get_nodes_view(self, collection_id: int, limit: int = 1000) -> list[NodeView]:
        nodes = self._node_service.get_nodes(collection_id, limit)
        return self._node_view_builder.to_views(nodes)

    def get_node_view(self, node_id: int) -> NodeView:
        node = self._node_service.get_node(node_id)
        return self._node_view_builder.to_view(node)
        
    def create_node(self, collection_id: int, data: NodeCreate, tz_offset_min: int) -> Node:
        if isinstance(data, NodeCreateFromUrl):
            return self._create_node_from_url_usecase.execute(collection_id, data.url, tz_offset_min)
        else:
            raise UnknownRessourceTypeError(type(data).__name__)

    def update_node(self, node_id, data: NodeUpdate) -> Node:
        node = self._node_service.get_node(node_id)
        if node.type == NodeType.FRAGMENT:
            return self._fragment_service.update_fragment(node_id, data)
        elif node.type == NodeType.SPORE:
            return self._spore_service.update_spore(node_id, data)
        else:
            raise NotAKnownType(node_id, node.type)

    def create_node_to_view(self, collection_id: int, data: NodeCreate, tz_offset_min: int) -> NodeView:
        return self._node_view_builder.to_view(self.create_node(collection_id, data, tz_offset_min))

    def update_node_to_view(self, node_id: int, data: NodeUpdate) -> NodeView:
        return self._node_view_builder.to_view(self.update_node(node_id, data))

    def reprioritise_node_to_view(self, collection_id: int, node_id: int, target_node_priority: float) -> NodeView:
        self._priority_service.reprioritise_node(collection_id, node_id, target_node_priority)
        node = self._node_service.get_node(node_id)
        return self._node_view_builder.to_view(node)
    
    def create_extract(self, col_id: int, extract_type: int, source_node_id: int, text: str, field: int, start_index: int, end_index: int, tz_offset_min: int) -> ExtractResult:
        source_node = self._node_service.get_node(source_node_id)
        
        self._check_text_match(source_node, field, start_index, end_index, text)
        
        if "\n" in text and extract_type == NodeType.SPORE: # I forgot why
            raise ExtractError("EXTRACT_ERROR", "Spore can't include new lines")            
        if source_node.type != NodeType.FRAGMENT:
            raise InvalidSourceNodeType(source_node_id, extract_type)
        
        if extract_type == NodeType.FRAGMENT:
            extract = self._fragment_service.create_fragment(col_id, text, source_node_id, tz_offset_min)
        elif extract_type == NodeType.SPORE:
            due = start_of_local_tomorrow_ms(tz_offset_min)
            source_content = next(iter(source_node.content.fields.values())) # temp, need simplification
            spore = self._spore_service.create_spore(col_id, due, source_content, source_node_id)
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
            source = self._fragment_service.emphasize_region(source_node_id, extract_type, str(field), start_index, end_index, text)
        except Exception as e:
            logger.warning(f"Failed to emphasize region in parent (id {source_node_id}), but extract is valid: {e}")
        
        return ExtractResult(
            extract_node=self._node_view_builder.to_view(extract),
            source_node=self._node_view_builder.to_view(source),
        )

    def restore_nodes_to_views(
        self,
        node_id: int,
        restore_ancestors: bool = False,
        restore_descendants: bool = False,
    ) -> list[NodeView]:
        node = self._node_service.restore_node(node_id)
        restored = [node]
        if restore_ancestors:
            restored += self._node_service.restore_ancestors(node_id)
        if restore_descendants:
            restored += self._node_service.restore_descendants(node_id)

        for n in restored:
            # Ensure restored node positions do not conflict with existing collection nodes
            current_priority = self._priority_service.get_priority(n.collection_id, n.id)
            new_position = self._priority_service.get_position_for_priority(n.collection_id, current_priority)
            n.position = new_position
            self._node_service.update_position(n.id, new_position)

        return self._node_view_builder.to_views(restored)

    def get_root_node(self, node_id: int) -> NodeView:
        root_node = self._node_service.get_root_node(node_id)
        return self._node_view_builder.to_view(root_node)

    def get_priorities(self, col_id: int) -> dict[int, float]:
        return self._priority_service.get_priorities(col_id)

    def reschedule_node_to_view(self, col_id: int, node_id: int, local_date_iso: str, tz_offset_min: int) -> NodeView:
        node = self._reschedule_node_usecase.execute(col_id, node_id, local_date_iso, tz_offset_min)
        return self._node_view_builder.to_view(node)

    def remove_links_to_view(self, col_id: int, node_id: int, text: str, field: int, start_index: int, end_index: int) -> NodeView:
        node = self._node_service.get_node(node_id)
        self._check_text_match(node, field, start_index, end_index, text)
        node = self._node_format_service.remove_links(node, str(field), start_index, end_index, text)
        updated = self._node_service.update(node_id, NodeUpdate(content=node.content))
        return self._node_view_builder.to_view(updated)

    def get_outline_for_node(self, col_id: int, node_id: int) -> Outline:
        node = self._node_service.get_node(node_id)
        return self._get_outline_usecase.execute(node)

    def split_node_to_views(self, col_id: int, node_id: int, tz_offset_min: int, level: int) -> list[NodeView]:
        node = self._node_service.get_node(node_id)
        content = node.content.get_first_field()
        if content is None:
            raise EmptyField(node_id, "0")
        children = self._split_node.execute(col_id, node_id, tz_offset_min, level)
        self._fragment_service.emphasize_region(node_id, NodeType.FRAGMENT, "0", 0, len(content))
        source_node = self._fragment_service.dismiss(node_id)
        nodes = children + [source_node]
        return self._node_view_builder.to_views(nodes)
