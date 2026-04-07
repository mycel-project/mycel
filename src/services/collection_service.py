from typing import Optional
from dataclasses import  asdict

from src.db import Db
from src.models.collection import Collection
from src.repositories.collection_repository import CollectionRepository
from src.models.collection_list_view import CollectionListView
from src.models.collection_conf import CollectionConf
from src.models.collection_conf_update import CollectionConfUpdate
from src.models.fsrs_conf import FsrsConf
from src.models.fsrs_conf_update import FsrsConfUpdate


class CollectionService:
    def __init__(self, db: Db):
        self._repo = CollectionRepository(db)

    def create_collection(
        self,
        name: str
    ) -> Collection:
        conf = self.create_default_collection_conf()
        fsrsconf = self.create_default_fsrs_conf()
        return self._repo.create(
            name=name,
            conf=conf,
            fsrsconf=fsrsconf
        )

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
        return FsrsConf(
            params="light"
        )
    
    def update_fsrs_conf(self, collection_id: int, update: FsrsConfUpdate):
        collection = self._repo.get(collection_id)
        if not collection:
            raise ValueError("Collection not found")

        for key, value in asdict(update).items():
            if value is not None:
                setattr(collection.fsrsconf, key, value)

        self._repo.update(
            id=collection_id,
            fsrsconf=collection.fsrsconf
        )

    def get_collections(self) -> list[CollectionListView]:
        collections = self._repo.list()
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

    def get_collection_detailed(self, col_id: int) -> Optional[Collection]:
        collection = self._repo.get(col_id)
        print(collection)
        return collection

    def update_configs(self, col_id: int, config_model: str, updates: dict) -> None:
        if config_model=="collection":
            data = CollectionConfUpdate(**updates)
            self.update_collection_conf(col_id, data)
        elif config_model=="fsrs":
            data = FsrsConfUpdate(**updates)
            self.update_fsrs_conf(col_id, data)
                
