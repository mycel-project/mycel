from src.schemas.collection_update import CollectionUpdate
from src.schemas.collection_view import CollectionView
from src.services.collection_service import CollectionService


class CollectionOrchestrator:
    def __init__(
        self,
        collection_service: CollectionService,
    ):
        self._collection_service = collection_service

    def create_collection(self, name: str, user_id: str) -> CollectionView:
        collection = self._collection_service.create_collection(name=name, user_id=user_id)
        return self._collection_service.to_view(collection)

    def get_collections(self, user_id: str) -> list[CollectionView]:
        collections = self._collection_service.get_collections(user_id)
        return self._collection_service.to_views(collections)

    def update_collection(self, user_id: str, collection_id: str, updates: CollectionUpdate) -> CollectionView:
        collection = self._collection_service.update(user_id=user_id, collection_id=collection_id, updates=updates)
        return self._collection_service.to_view(collection)

    def delete_collection(self, user_id: str, collection_id: str) -> None:
        self._collection_service.delete_collection(user_id, collection_id)
