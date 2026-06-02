from src.schemas.collection_view import CollectionView
from src.services.collection_service import CollectionService


class CollectionOrchestrator:
    def __init__(
        self,
        collection_service: CollectionService,
    ):
        self._collection_service = collection_service

    def create_collection(self, name: str, user_id: int) -> CollectionView:
        collection = self._collection_service.create_collection(name=name, user_id=user_id)
        return self._collection_service.to_view(collection)
