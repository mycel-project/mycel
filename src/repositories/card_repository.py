import json
import time
from typing import Optional

from src.db import Db
from src.models.card import Card, NEW


class CardRepository:
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Card:
        return Card(
            id=row["id"],
            collection_id=row["collection_id"],
            note_id=row["note_id"],
            type=row["type"],
            queue=row["queue"],
            due=row["due"],
            interval=row["interval"],
            ease_factor=row["ease_factor"],
            stability=row["stability"],
            difficulty=row["difficulty"],
            fsrs_step=row["fsrs_step"],
            reps=row["reps"],
            lapses=row["lapses"],
            last_review=row["last_review"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            flags=row["flags"],
            data=json.loads(row["data"]),
            tags=json.loads(row["tags"]),
        )

    def create(
        self,
        collection_id: int,
        data: dict,
        tags: list | None = None,
        note_id: int | None = None,
    ) -> Card:
        now = int(time.time() * 1000)
        card = Card(
            id=now,
            collection_id=collection_id,
            note_id=note_id,
            type=NEW,
            queue=NEW,
            due=now,
            interval=0,
            ease_factor=2.5,
            reps=0,
            lapses=0,
            last_review=None,
            created_at=now,
            updated_at=now,
            flags=0,
            data=data,
            tags=tags or [],
        )
        self.db.execute(
            """INSERT INTO cards
               (id, collection_id, note_id, type, queue, due, interval, ease_factor,
                stability, difficulty, fsrs_step,
                reps, lapses, last_review, created_at, updated_at, flags, data, tags)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                card.id, card.collection_id, card.note_id, card.type, card.queue,
                card.due, card.interval, card.ease_factor,
                card.stability, card.difficulty, card.fsrs_step,
                card.reps, card.lapses, card.last_review,
                card.created_at, card.updated_at, card.flags,
                json.dumps(card.data), json.dumps(card.tags),
            ),
        )
        return card

    def get(self, id: int) -> Optional[Card]:
        row = self.db.fetch_one("SELECT * FROM cards WHERE id = ?", (id,))
        return self._row_to_model(row) if row else None

    def update(self, card: Card) -> None:
        now = int(time.time() * 1000)
        card.updated_at = now
        self.db.execute(
            """UPDATE cards SET
               type=?, queue=?, due=?, interval=?, ease_factor=?,
               stability=?, difficulty=?, fsrs_step=?,
               reps=?, lapses=?, last_review=?, updated_at=?, flags=?, data=?, tags=?
               WHERE id=?""",
            (
                card.type, card.queue, card.due, card.interval, card.ease_factor,
                card.stability, card.difficulty, card.fsrs_step,
                card.reps, card.lapses, card.last_review, card.updated_at, card.flags,
                json.dumps(card.data), json.dumps(card.tags), card.id,
            ),
        )

    def delete(self, id: int) -> None:
        self.db.execute("DELETE FROM cards WHERE id = ?", (id,))

    def get_due(self, collection_id: int, now_ms: int | None = None) -> list[Card]:
        now_ms = now_ms or int(time.time() * 1000)
        rows = self.db.fetch_all(
            "SELECT * FROM cards WHERE collection_id = ? AND due <= ? ORDER BY due",
            (collection_id, now_ms),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_collection(self, collection_id: int) -> list[Card]:
        rows = self.db.fetch_all(
            "SELECT * FROM cards WHERE collection_id = ? ORDER BY created_at",
            (collection_id,),
        )
        return [self._row_to_model(r) for r in rows]
