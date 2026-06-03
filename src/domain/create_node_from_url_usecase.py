from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.domain.domain_exceptions import InvalidUrl
from src.models.node import Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
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

    def execute(self, collection_id: str, url: str, tz_offset: int = 0) -> Node:
        if not is_valid_url(url):
            raise InvalidUrl(url)

        ressource = self._ressource_service.get_ressource_from_url(url)
        
        return self._create_fragment.execute(
            collection_id=collection_id,
            content=NodeContent.from_input(ressource.content),
            data=NodeData(title=ressource.title, src=ressource.source),
            tz_offset=tz_offset,
        )
