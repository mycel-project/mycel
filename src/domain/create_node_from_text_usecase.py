from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.models.node import Node, NodeFields
from src.models.node_create import NodeCreateFromText
from src.models.node_data import NodeData, NodeSource
from src.models.template import DefaultTemplate


class CreateNodeFromTextUseCase:
    def __init__(
        self,
        create_fragment_use_case: CreateFragmentUseCase,
    ):
        self._create_fragment = create_fragment_use_case

    def execute(self, user_id: str, collection_id: str, data: NodeCreateFromText, tz_offset: int = 0) -> Node:        
        return self._create_fragment.execute(
            user_id=user_id,
            collection_id=collection_id,
            template_id=DefaultTemplate.FRAGMENT_BASIC,
            fields=NodeFields(root={"content": data.content}),
            data=NodeData(title=data.title, source=data.source),
            tz_offset=tz_offset,
        )
