import json
import time
from typing import Optional

from src.db import Db
from src.models.node import Node, NEW


class NodeRepository:
    """
    Data access
    """
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Node:
        return Node(
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
            order_key=row["order_key"],
        )

    def create(
        self,
        collection_id: int,
        data: dict,
        tags: list | None = None,
        note_id: int | None = None,
        order_key: str | None = None,
    ) -> Node:
        now = int(time.time() * 1000)
        node = Node(
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
            order_key=order_key,
        )
        self.db.execute(
            """INSERT INTO nodes
               (id, collection_id, note_id, type, queue, due, interval, ease_factor,
                stability, difficulty, fsrs_step,
                reps, lapses, last_review, created_at, updated_at, flags, data, tags, order_key)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                node.id, node.collection_id, node.note_id, node.type, node.queue,
                node.due, node.interval, node.ease_factor,
                node.stability, node.difficulty, node.fsrs_step,
                node.reps, node.lapses, node.last_review,
                node.created_at, node.updated_at, node.flags,
                json.dumps(node.data), json.dumps(node.tags), node.order_key,
            ),
        )
        return node

    def get(self, id: int) -> Optional[Node]:
        row = self.db.fetch_one("SELECT * FROM nodes WHERE id = ?", (id,))
        return self._row_to_model(row) if row else None

    def update(self, node: Node) -> None:
        now = int(time.time() * 1000)
        node.updated_at = now
        self.db.execute(
            """UPDATE nodes SET
               type=?, queue=?, due=?, interval=?, ease_factor=?,
               stability=?, difficulty=?, fsrs_step=?,
               reps=?, lapses=?, last_review=?, updated_at=?, flags=?, data=?, tags=?
               WHERE id=?""",
            (
                node.type, node.queue, node.due, node.interval, node.ease_factor,
                node.stability, node.difficulty, node.fsrs_step,
                node.reps, node.lapses, node.last_review, node.updated_at, node.flags,
                json.dumps(node.data), json.dumps(node.tags), node.id,
            ),
        )

    def delete(self, id: int) -> None:
        self.db.execute("DELETE FROM nodes WHERE id = ?", (id,))

    def get_due(self, collection_id: int, now_ms: int | None = None) -> list[Node]:
        now_ms = now_ms or int(time.time() * 1000)
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? AND due <= ? ORDER BY due",
            (collection_id, now_ms),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_collection(self, collection_id: int) -> list[Node]:
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? ORDER BY order_key",
            (collection_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_tail_key(self, collection_id: int) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT MAX(order_key) FROM nodes WHERE collection_id = ?",
            (collection_id,),
        )
        return row[0] if row and row[0] is not None else None

    def get_neighbor_keys(
        self,
        collection_id: int,
        before_id: int | None,
        after_id: int | None,
    ) -> tuple[Optional[str], Optional[str]]:
        a_key = None
        b_key = None
        if before_id is not None:
            row = self.db.fetch_one(
                "SELECT order_key FROM nodes WHERE id = ? AND collection_id = ?",
                (before_id, collection_id),
            )
            if row is None:
                raise ValueError(f"Node {before_id} not found in collection {collection_id}")
            a_key = row["order_key"]
        if after_id is not None:
            row = self.db.fetch_one(
                "SELECT order_key FROM nodes WHERE id = ? AND collection_id = ?",
                (after_id, collection_id),
            )
            if row is None:
                raise ValueError(f"Node {after_id} not found in collection {collection_id}")
            b_key = row["order_key"]
        return a_key, b_key

    def get_nodes_after(
        self,
        collection_id: int,
        order_key: Optional[str],
        limit: int,
    ) -> list[Node]:
        if order_key is None:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? ORDER BY order_key LIMIT ?",
                (collection_id, limit),
            )
        else:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? AND order_key > ? ORDER BY order_key LIMIT ?",
                (collection_id, order_key, limit),
            )
        return [self._row_to_model(r) for r in rows]

    def get_predecessor_key(
        self,
        collection_id: int,
        order_key: str,
        exclude_id: int,
    ) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT order_key FROM nodes "
            "WHERE collection_id = ? AND order_key < ? AND id != ? "
            "ORDER BY order_key DESC LIMIT 1",
            (collection_id, order_key, exclude_id),
        )
        return row["order_key"] if row else None

    def get_successor_key(
        self,
        collection_id: int,
        order_key: str,
        exclude_id: int,
    ) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT order_key FROM nodes "
            "WHERE collection_id = ? AND order_key > ? AND id != ? "
            "ORDER BY order_key ASC LIMIT 1",
            (collection_id, order_key, exclude_id),
        )
        return row["order_key"] if row else None

    def get_all_order_keys(self, collection_id: int) -> list[tuple[int, str]]:
        """Returns (id, order_key) sorted by order_key."""
        rows = self.db.fetch_all(
            "SELECT id, order_key FROM nodes WHERE collection_id = ? ORDER BY order_key",
            (collection_id,),
        )
        return [(row["id"], row["order_key"]) for row in rows]

    def update_order_key(self, node_id: int, order_key: str) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET order_key = ?, updated_at = ? WHERE id = ?",
            (order_key, now, node_id),
        )
