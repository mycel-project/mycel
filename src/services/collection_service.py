from typing import Optional
from dataclasses import  asdict

from src.domain.domain_exceptions import NoCollectionFound
from src.models.collection import Collection
from src.repositories.collection_repository import CollectionRepository
from src.schemas.collection_update import CollectionUpdate
from src.schemas.collection_view import CollectionView
from src.models.collection_conf import CollectionConf
from src.models.fsrs_conf import FsrsConf
from src.schemas import FsrsConfUpdate, CollectionConfUpdate
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
        user_id: int,
        id: Optional[int] = None,

    ) -> Collection:
        return self._repo.create(
            user_id=user_id,
            name=name,
            conf=CollectionConf(),
            fsrsconf=FsrsConf(),
            id=id,
        )

    def get_collection(self, collection_id: int) -> Collection:
        collection = self._repo.get(collection_id)
        if collection is None:
            raise NoCollectionFound(collection_id)
        return collection

    def get_collections(self, user_id) -> list[Collection]:
        return self._repo.list(user_id)

    def delete_collection(self, collection_id: int) -> None:
        self._repo.delete(collection_id)

    def get_fsrs_conf(self, collection_id: int) -> FsrsConf:
        collection = self._repo.get(collection_id)
        if not collection:
            raise ValueError("Collection not found")
        return collection.fsrsconf

    def to_view(self, collection: Collection) -> CollectionView:
        return CollectionView(
            id=collection.id,
            name=collection.name,
        )

    def to_views(self, collections: list[Collection]) -> list[CollectionView]:
        return [self.to_view(c) for c in collections]

    def update(self, collection_id: int, updates: CollectionUpdate) -> Collection:
        collection = self.get_collection(collection_id)
        
        # Fields explicitly provided in updates (even if set to None) will overwrite existing values (due to model_fiels_set).
        # To prevent setting a field to None, do not include it in the update payload.
        for field in updates.model_fields_set: 
            value = getattr(updates, field)
            setattr(collection, field, value)

        self._repo.update(collection)
        return collection
