import time
import json
from typing import Optional
from uuid import uuid4
from src.db import Db
from src.models.collection import Collection
from src.models.collection_conf import CollectionConf
from src.models.algo_conf import AlgoConf

class CollectionRepository:
    def __init__(self, db: Db):
        self.db = db

    def create(self, user_id: str, name: str, conf: CollectionConf, algoconf: AlgoConf, id: Optional[str] = None) -> Collection:
        now = int(time.time() * 1000)
        if id is None:
            id = str(uuid4())
        self.db.execute(
            """INSERT INTO collections (id, user_id, name, created_at, updated_at, conf, algoconf)
               VALUES (:id, :user_id, :name, :created_at, :updated_at, :conf, :algoconf)""",
            {"id": id, "user_id": user_id, "name": name, "created_at": now, "updated_at": now,
             "conf": json.dumps(conf.model_dump()), "algoconf": json.dumps(algoconf.model_dump())},
        )
        return Collection(id=id, user_id=user_id, name=name, created_at=now, updated_at=now, conf=conf, algoconf=algoconf)

    def get(self, user_id: str, id: str) -> Optional[Collection]:
            row = self.db.fetch_one("SELECT * FROM collections WHERE id = :id AND user_id = :user_id", {"id": id, "user_id": user_id})
            return Collection.from_db(row) if row else None

    def update(self, user_id: str, collection: Collection) -> None:
            now = int(time.time() * 1000)
            self.db.execute(
                """UPDATE collections SET name=:name, conf=:conf, algoconf=:algoconf, updated_at=:now WHERE id=:id AND user_id=:user_id""",
                {"name": collection.name, "conf": json.dumps(collection.conf.model_dump()),
                 "algoconf": json.dumps(collection.algoconf.model_dump()), "now": now, "id": collection.id, "user_id": user_id},
            )

    def delete(self, user_id: str, id: str) -> None:
            self.db.execute(
                "DELETE FROM collections WHERE id = :id AND user_id = :user_id",
                {"id": id, "user_id": user_id}
            )

    def list(self, user_id: str) -> list[Collection]:
        rows = self.db.fetch_all(
            "SELECT * FROM collections WHERE user_id = :user_id ORDER BY created_at",
            {"user_id": user_id}
        )
        return [Collection.from_db(r) for r in rows]
