import time
from typing import Optional

from src.db import Db
from src.models.collection import Collection


class CollectionRepository:
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Collection:
        return Collection(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, name: str) -> Collection:
        now = int(time.time() * 1000)
        self.db.execute(
            "INSERT INTO collections (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (now, name, now, now),
        )
        return Collection(id=now, name=name, created_at=now, updated_at=now)

    def get(self, id: int) -> Optional[Collection]:
        row = self.db.fetch_one("SELECT * FROM collections WHERE id = ?", (id,))
        return self._row_to_model(row) if row else None

    def update(self, id: int, name: str) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE collections SET name = ?, updated_at = ? WHERE id = ?",
            (name, now, id),
        )

    def delete(self, id: int) -> None:
        self.db.execute("DELETE FROM collections WHERE id = ?", (id,))

    def list(self) -> list[Collection]:
        rows = self.db.fetch_all("SELECT * FROM collections ORDER BY created_at")
        return [self._row_to_model(r) for r in rows]
