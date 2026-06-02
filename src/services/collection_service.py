from typing import Optional
from dataclasses import  asdict

from src.db import Db
from src.domain.domain_exceptions import NoCollectionFound
from src.models.collection import Collection
from src.repositories.collection_repository import CollectionRepository
from src.schemas.collection_list_view import CollectionListView
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
        conf = self.create_default_collection_conf() # Can juste do conf = CollectionConf() if it has default values in model
        fsrsconf = self.create_default_fsrs_conf() # //
        return self._repo.create(
            user_id=user_id,
            name=name,
            conf=conf,
            fsrsconf=fsrsconf,
            id=id,
        )

    def get_collection(self, collection_id: int) -> Collection:
        collection = self._repo.get(collection_id)
        if collection is None:
            raise NoCollectionFound(collection_id)
        return collection

    def delete_collection(self, collection_id: int) -> None:
        self._repo.delete(collection_id)

    def create_default_collection_conf(self) -> CollectionConf:
        return CollectionConf(
            theme="light"
        )

    def update_collection_conf(self, collection_id: int, update: CollectionConfUpdate):
        collection = self._repo.get(collection_id)
        if not collection:
            raise ValueError("Collection not found")

        for key, value in asdict(update).items():
            if value is not None:
                setattr(collection.conf, key, value)

        self._repo.update(
            id=collection_id,
            conf=collection.conf
        )

    def create_default_fsrs_conf(self) -> FsrsConf:
        return FsrsConf()
    
    def update_fsrs_conf(self, collection_id: int, update: FsrsConfUpdate):
        collection = self._repo.get(collection_id)
        if not collection:
            raise ValueError("Collection not found")

        for key, value in update.model_dump(exclude_none=True).items():
            setattr(collection.fsrsconf, key, value)

        self._repo.update(
            id=collection_id,
            fsrsconf=collection.fsrsconf
        )

    def get_fsrs_conf(self, collection_id: int) -> FsrsConf:
        collection = self._repo.get(collection_id)
        if not collection:
            raise ValueError("Collection not found")
        return collection.fsrsconf

    def get_collections(self, user_id) -> list[CollectionListView]:
        collections = self._repo.list(user_id)
        return [
            CollectionListView(
                id=c.id,
                name=c.name
            )
            for c in collections
        ]

    def rename_collection(self, collection_id: int, new_name: str) -> None:
        collection = self._repo.get(collection_id)
        if not collection:
            raise ValueError("Collection not found")

        self._repo.update(
            id=collection_id,
            name=new_name,
        )

    def get_collection_details(self, col_id: int) -> Optional[Collection]:
        collection = self._repo.get(col_id)
        return collection

    def update_configs(self, col_id: int, new_config: ConfigUpdate) -> None:

        if new_config.collection is not None:
            data = CollectionConfUpdate(**new_config.collection)
            self.update_collection_conf(col_id, data)

        if new_config.fsrs is not None:
            data = FsrsConfUpdate(**new_config.fsrs)
            self.update_fsrs_conf(col_id, data)
