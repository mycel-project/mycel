from src.domain.create_node_usecase import CreateNodeUseCase
from src.domain.domain_exceptions import InvalidUrl
from src.models.node import Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.services.ressource_service import RessourceService
from src.types.node_type import NodeType
from src.utils.time import start_of_local_tomorrow_ms
from src.utils.url import is_valid_url


class CreateNodeFromUrlUseCase:
    def __init__(
        self,
        create_node_use_case: CreateNodeUseCase,
        ressource_service: RessourceService,
    ):
        self._create_node = create_node_use_case
        self._ressource_service = ressource_service

    def execute(self, collection_id: int, url: str, tz_offset: int = 0) -> Node:
        if not is_valid_url(url):
            raise InvalidUrl(url)

        ressource = self._ressource_service.get_ressource_from_url(url)

        due = start_of_local_tomorrow_ms(tz_offset)
        
        return self._create_node.execute(
            collection_id=collection_id,
            type=NodeType.FRAGMENT,
            content=NodeContent.from_input(ressource.content),
            data=NodeData(title=ressource.title, src=ressource.source),
            due=due,
        )
