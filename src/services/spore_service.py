from typing import Optional

from src.core.regex import CLOZE_PATTERN
from src.domain.create_spore_usecase import CreateSporeUseCase
from src.domain.domain_exceptions import ClozeValidationError, InvalidNodeUpdate, NoClozeFieldError, NotASpore
from src.models.template import DefaultTemplate, SporeClozeTemplate
from src.schemas.node_update import NodeUpdate
from src.services.node_format_service import NodeFormatService
from src.services.node_service import NodeService
from src.models.node import Node, NodeFields, NodeType
from src.services.user_service import UserService

class SporeService:
    def __init__(
        self,
        user_service: UserService,
        node_service: NodeService,
        node_format_service: NodeFormatService,
        create_spore_use_case: CreateSporeUseCase,
    ):
        self._user_service = user_service
        self._node_service = node_service
        self._node_format_service = node_format_service
        self._create_spore = create_spore_use_case

    def create_spore(self, user_id: str, col_id: str, content: str, due: Optional[int] = None, parent_id: Optional[str] = None, tz_offset: int = 0) -> Node:
        return self._create_spore.execute(
            user_id=user_id,
            collection_id=col_id,
            fields=NodeFields(root={"cloze": content}),
            template_id=DefaultTemplate.SPORE_CLOZE,
            parent_id=parent_id,
            tz_offset=tz_offset,
            due=due,
        )

    def update_spore(self, user_id: str, node_id: str, data: NodeUpdate) -> Node:
        node = self._node_service.get_node(node_id)
        user = self._user_service.get_user(user_id)
        if node.base_for != NodeType.SPORE:
            raise NotASpore(node_id)
        fields = data.fields
        if fields is not None:
            template = user.templates.root[node.template_id]
            if isinstance(template, SporeClozeTemplate):
                try:
                    self.validate_spore_content(fields["cloze"])
                except ValueError as e:
                    raise InvalidNodeUpdate(node_id, node.base_for, fields, str(e)) from ClozeValidationError()
        return self._node_service.update(node_id, data)

    def validate_spore_content(self, text: str):
        if not self.has_cloze(text):
            raise NoClozeFieldError(text)

    def has_cloze(self, content: str, slot: Optional[int] = None) -> bool:
        """
        if slot is none, search for any slot, at least one
        """
        matches = CLOZE_PATTERN.finditer(content)
        if slot is None:
            return any(True for _ in matches)
        return any(int(m.group(1)) == slot for m in matches)

    def cloze_region(self, node_id: str, text: str, field: str, start: int, end: int) -> Node:
        node = self._node_service.get_node(node_id)

        clozed_node = self._node_format_service.cloze_region(node, field, start, end, text)
        content = clozed_node.fields[field]
        if not self.has_cloze(content):
            raise NoClozeFieldError(content)
        return self._node_service.update(
            node_id,
            NodeUpdate(fields=clozed_node.fields)
        )

    def remove_extract_formatting(self, node_id: str, field: str) -> Node:
        node = self._node_service.get_node(node_id)

        field_content = node.fields[field]
        
        text_without_emphasis = self._node_format_service.remove_spore_emphasis(node, field_content)
        fully_cleaned_text = self._node_format_service.remove_fragment_emphasis(node, text_without_emphasis, r"\{\{c\d+::\s*")

        node.fields[field] = fully_cleaned_text
        return self._node_service.update(
            node.id,
            NodeUpdate(fields=node.fields)
        )
