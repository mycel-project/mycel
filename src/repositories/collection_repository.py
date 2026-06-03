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

    def _row_to_model(self, row) -> Collection:
        return Collection(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            conf=CollectionConf.model_validate(
                json.loads(row["conf"]) if isinstance(row["conf"], str) else row["conf"]
            ),
            algoconf=AlgoConf.model_validate(
                json.loads(row["algoconf"]) if isinstance(row["algoconf"], str) else row["algoconf"]
            ),
        )

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

    def get(self, id: str) -> Optional[Collection]:
        row = self.db.fetch_one("SELECT * FROM collections WHERE id = :id", {"id": id})
        return self._row_to_model(row) if row else None

    def update_timestamp(self, id: str) -> None:
        now = int(time.time() * 1000)
        self.db.execute("UPDATE collections SET updated_at = :now WHERE id = :id", {"now": now, "id": id})

    def update(self, collection: Collection) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            """UPDATE collections SET name=:name, conf=:conf, algoconf=:algoconf, updated_at=:now WHERE id=:id""",
            {"name": collection.name, "conf": json.dumps(collection.conf.model_dump()),
             "algoconf": json.dumps(collection.algoconf.model_dump()), "now": now, "id": collection.id},
        )

    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM collections WHERE id = :id", {"id": id})

    def list(self, user_id: str) -> list[Collection]:
        rows = self.db.fetch_all(
            "SELECT * FROM collections WHERE user_id = :user_id ORDER BY created_at",
            {"user_id": user_id}
        )
        return [self._row_to_model(r) for r in rows]
