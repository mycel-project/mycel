from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.domain.get_outline_usecase import GetOutlineUseCase
from src.models.node import Node
from src.services.node_service import NodeService


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

    def execute(self, collection_id: int, node_id: int, tz_offset: int, level: int) -> list[Node]:
        node = self._node_service.get_node(node_id)
        text = node.content.get_first_field() or "" if node.content else ""
        outline = self._get_outline.execute(node)
        entries = [e for e in outline.entries if e.level <= level]
        results = []
        intro = text[:entries[0].offset].strip() if entries else text.strip()
        if intro:
            node_result = self._create_fragment.execute(
                collection_id, intro, parent_id=node.id, tz_offset=tz_offset
            )
            results.append(node_result)
        for i, entry in enumerate(entries):
            start = entry.offset
            end = entries[i + 1].offset if i + 1 < len(entries) else len(text)
            content = text[start:end].strip()
            if content:
                node_result = self._create_fragment.execute(
                    collection_id, content, parent_id=node.id, tz_offset=tz_offset
                )
                results.append(node_result)
        return results
