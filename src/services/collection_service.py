from typing import Optional
from dataclasses import  asdict

from src.domain.domain_exceptions import NoCollectionFound
from src.models.collection import Collection
from src.repositories.collection_repository import CollectionRepository
from src.schemas.collection_update import CollectionUpdate
from src.schemas.collection_view import CollectionView
from src.models.collection_conf import CollectionConf
from src.models.algo_conf import AlgoConf
from src.schemas import AlgoConfUpdate, CollectionConfUpdate
from src.schemas.config_update import ConfigUpdate


class CollectionService:
    """
    Application service for collection management.

    Provides a higher-level API over CollectionRepository:
    - creation of collections
    - retrieval of collections
    - business rules related to collections lifecycle
    """
    def __init__(self, collection_repository: CollectionRepository):
        self._repo = collection_repository

    def create_collection(
        self,
        name: str,
        user_id: str,
        id: Optional[str] = None,

    ) -> Collection:
        return self._repo.create(
            user_id=user_id,
            name=name,
            conf=CollectionConf(),
            algoconf=AlgoConf(),
            id=id,
        )

    def get_collection(self, user_id: str, collection_id: str) -> Collection:
        collection = self._repo.get(user_id, collection_id)
        if collection is None:
            raise NoCollectionFound(collection_id)
        return collection

    def get_collections(self, user_id: str) -> list[Collection]:
        return self._repo.list(user_id)

    def delete_collection(self, user_id: str, collection_id: str) -> None:
        self._repo.delete(user_id, collection_id)

    def get_algo_conf(self, user_id: str, collection_id: str) -> AlgoConf:
        collection = self._repo.get(user_id, collection_id)
        if not collection:
            raise ValueError("Collection not found")
        return collection.algoconf

    def to_view(self, collection: Collection) -> CollectionView:
        return CollectionView(
            id=collection.id,
            name=collection.name,
            conf=collection.conf,
            algoconf=collection.algoconf,
            created_at=collection.created_at,
        )

    def to_views(self, collections: list[Collection]) -> list[CollectionView]:
        return [self.to_view(c) for c in collections]

    def update(self, user_id: str, collection_id: str, updates: CollectionUpdate) -> Collection:
        collection = self.get_collection(user_id, collection_id)
        
        # Fields explicitly provided in updates (even if set to None) will overwrite existing values (due to model_fiels_set).
        # To prevent setting a field to None, do not include it in the update payload.
        for field in updates.model_fields_set: 
            value = getattr(updates, field)
            setattr(collection, field, value)

        self._repo.update(user_id, collection)
        return collection
