from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.domain.domain_exceptions import InvalidUrl
from src.models.node import Node, NodeFields
from src.models.node_data import NodeData, NodeSource
from src.models.template import DefaultTemplate
from src.services.ressource_service import RessourceService
from src.utils.url import is_valid_url


class CreateNodeFromUrlUseCase:
    def __init__(
        self,
        create_fragment_use_case: CreateFragmentUseCase,
        ressource_service: RessourceService,
    ):
        self._create_fragment = create_fragment_use_case
        self._ressource_service = ressource_service

    def execute(self, user_id: str, collection_id: str, url: str, tz_offset: int = 0) -> Node:
        if not is_valid_url(url):
            raise InvalidUrl(url)

        ressource = self._ressource_service.get_ressource_from_url(url)
        
        return self._create_fragment.execute(
            user_id=user_id,
            collection_id=collection_id,
            template_id=DefaultTemplate.FRAGMENT_BASIC,
            fields=NodeFields(root={"content": ressource.content}),
            data=NodeData(title=ressource.title, source=NodeSource(url=ressource.source)),
            tz_offset=tz_offset,
        )
