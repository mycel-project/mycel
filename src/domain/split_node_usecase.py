from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.domain.domain_exceptions import NoHeadingToSplit
from src.domain.get_outline_usecase import GetOutlineUseCase
from src.models.node import Node, NodeFields
from src.services.node_service import NodeService
from src.utils.time import start_of_local_tomorrow_ms


class SplitNodeUseCase:
    def __init__(
        self,
        node_service: NodeService,
        create_fragment_usecase: CreateFragmentUseCase,
        get_outline_usecase: GetOutlineUseCase
    ):
        self._node_service = node_service
        self._create_fragment = create_fragment_usecase
        self._get_outline = get_outline_usecase

    def execute(self, user_id: str, collection_id: str, node_id: str, tz_offset: int, level: int) -> list[Node]:
        node = self._node_service.get_node(node_id)
        text = node.fields.get_content() or "" 
        outline = self._get_outline.execute(node)
        entries = [e for e in outline.entries if e.level <= level]

        if not entries:
            raise NoHeadingToSplit(node_id, level)
        results = []

        intro = text[:entries[0].offset].strip() if entries else ""
        fragment_count = len(entries) + (1 if intro else 0)
        if fragment_count <= 1:
            raise NoHeadingToSplit(node_id, level)

        if intro:
            node_result = self._create_fragment.execute(
                user_id, collection_id, NodeFields.from_dict({"content": intro}), parent_id=node.id, tz_offset=tz_offset
            )
            results.append(node_result)

        due = start_of_local_tomorrow_ms(tz_offset)

        for i, entry in enumerate(entries):
            start = entry.offset
            end = entries[i + 1].offset if i + 1 < len(entries) else len(text)
            content = text[start:end].strip()
            if content:
                node_result = self._create_fragment.execute(
                    user_id, collection_id, NodeFields.from_dict({"content": content}), parent_id=node.id, tz_offset=tz_offset, due=due,
                )
                results.append(node_result)

        return results
