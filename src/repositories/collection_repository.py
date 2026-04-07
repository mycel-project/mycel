import time
import json
from typing import Optional

from src.db import Db
from src.models.collection import Collection
from src.models.collection_conf import CollectionConf
from src.models.fsrs_conf import FsrsConf


class CollectionRepository:
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Collection:
        return Collection(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            conf=CollectionConf.from_dict(
                json.loads(row["conf"]) if isinstance(row["conf"], str) else row["conf"]
            ),
            fsrsconf=FsrsConf.from_dict(json.loads(row["fsrsconf"]) if isinstance(row["fsrsconf"], str) else row["fsrsconf"]),
        )

    def create(
        self,
        name: str,
        conf: CollectionConf,
        fsrsconf: FsrsConf,
    ) -> Collection:
        now = int(time.time() * 1000)
        
        self.db.execute(
            "INSERT INTO collections (id, name, created_at, updated_at, conf, fsrsconf) VALUES (?, ?, ?, ?, ?, ?)",
            (now, name, now, now, json.dumps(conf.to_dict()), json.dumps(fsrsconf.to_dict())),
        )
        return Collection(
            id=now,
            name=name,
            created_at=now,
            updated_at=now,
            conf=conf,
            fsrsconf=fsrsconf
        )

    def get(self, id: int) -> Optional[Collection]:
        row = self.db.fetch_one("SELECT * FROM collections WHERE id = ?", (id,))
        return self._row_to_model(row) if row else None

    def update_timestamp(self, id: int) -> None:
        """Met à jour uniquement le champ updated_at"""
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE collections SET updated_at = ? WHERE id = ?",
            (now, id),
        )

    def update(
            self,
            id: int,
            name: Optional[str] = None,
            conf: Optional[CollectionConf] = None,
            fsrsconf: Optional[FsrsConf] = None
    ) -> None:
        now = int(time.time() * 1000)
        
        existing = self.get(id)
        if not existing:
            raise ValueError(f"Collection {id} not found")
        
        name = name if name is not None else existing.name
        conf = conf if conf is not None else existing.conf
        fsrsconf = fsrsconf if fsrsconf is not None else existing.fsrsconf
        
        self.db.execute(
            "UPDATE collections SET name = ?, conf = ?, fsrsconf = ?, updated_at = ? WHERE id = ?",
            (name, json.dumps(conf.to_dict()), json.dumps(fsrsconf.to_dict()), now, id),
        )

    def delete(self, id: int) -> None:
        self.db.execute("DELETE FROM collections WHERE id = ?", (id,))

    def list(self) -> list[Collection]:
        rows = self.db.fetch_all("SELECT * FROM collections ORDER BY created_at")
        return [self._row_to_model(r) for r in rows]
