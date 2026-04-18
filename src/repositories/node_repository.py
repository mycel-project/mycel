import json
import time
from typing import Optional

from src.db import Db
from src.models.node import Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData

class NodeRepository:
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Node:
        return Node(
            id=row["id"],
            collection_id=row["collection_id"],
            parent_id=row["parent_id"],
            type=row["type"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            data=NodeData.from_db(row["data"]),
            due=row["due"],
            state=row["state"],
            content=NodeContent.from_db(row["content"]),
            last_review=row["last_review"], 
            stability=row["stability"],
            difficulty=row["difficulty"],
            step=row["step"],
            priority=row["priority"],
    )

    def create(
        self,
        collection_id: int,
        content: NodeContent,
        data: Optional[NodeData],
        parent_id: Optional[int] = None,
        priority: Optional[str] = None,
        type: Optional[int] = None,
    ) -> Node:
        now = int(time.time() * 1000)
        node = Node(
            id=now,
            collection_id=collection_id,
            parent_id=parent_id,
            created_at=now,
            updated_at=now,
            data=data or NodeData(),
            due=now,
            content=content, 
            priority=priority,
            type=type
        )
        self.db.execute(
            """INSERT INTO nodes
               (id, collection_id, parent_id, type, created_at, updated_at, data, due, state, content, priority)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                node.id,
                node.collection_id,
                node.parent_id,
                node.type,
                node.created_at,
                node.updated_at,
                node.data.to_db(),
                node.due,
                node.state,
                node.content.to_db(),  
                node.priority,
            ),
        )
        return node
    
    def get(self, id: int) -> Optional[Node]:
        row = self.db.fetch_one("SELECT * FROM nodes WHERE id = ?", (id,))
        return self._row_to_model(row) if row else None

    def update(self, node: Node) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            """UPDATE nodes SET
               parent_id=?, type=?, due=?, state=?, content=?, 
               last_review=?, stability=?, difficulty=?, step=?, priority=?, updated_at=?, data=?
               WHERE id=?""",
            (
                node.parent_id,
                node.type,
                node.due,
                node.state,
                node.content.to_db(), 
                node.last_review,
                node.stability,
                node.difficulty,
                node.step,
                node.priority,
                now,
                node.data.to_db(),
                node.id,
            ),
        )

    def delete(self, id: int) -> None:
        self.db.execute("DELETE FROM nodes WHERE id = ?", (id,))

    def get_by_collection(self, collection_id: int, limit: Optional[int] = None) -> list[Node]:
        if limit:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? ORDER BY priority LIMIT ?",
                (collection_id, limit),
            )
        else:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? ORDER BY priority",
                (collection_id,),
            )
        return [self._row_to_model(r) for r in rows]

    def get_by_type(self, collection_id: int, type: int) -> list[Node]:
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? AND type = ? ORDER BY priority",
            (collection_id, type),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_state(self, collection_id: int, state: int) -> list[Node]:
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? AND state = ? ORDER BY priority",
            (collection_id, state),
        )
        return [self._row_to_model(r) for r in rows]

    def update_priority(self, node_id: int, priority: str) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET priority = ?, updated_at = ? WHERE id = ?",
            (priority, now, node_id),
        )

    def update_state(self, node_id: int, state: int) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET state = ?, updated_at = ? WHERE id = ?",
            (state, now, node_id),
        )

    def update_fsrs_params(
        self,
        node_id: int,
        stability: float,
        difficulty: float,
        step: int,
    ) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET stability = ?, difficulty = ?, step = ?, updated_at = ? WHERE id = ?",
            (stability, difficulty, step, now, node_id),
        )

    def update_last_review(self, node_id: int) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET last_review = ?, updated_at = ? WHERE id = ?",
            (now, now, node_id),
        )

    def get_predecessor_priority(
        self,
        collection_id: int,
        priority: str,
        exclude_id: int,
    ) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT priority FROM nodes "
            "WHERE collection_id = ? AND priority < ? AND id != ? "
            "ORDER BY priority DESC LIMIT 1",
            (collection_id, priority, exclude_id),
        )
        return row["priority"] if row else None

    def get_successor_priority(
        self,
        collection_id: int,
        priority: str,
        exclude_id: int,
    ) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT priority FROM nodes "
            "WHERE collection_id = ? AND priority > ? AND id != ? "
            "ORDER BY priority ASC LIMIT 1",
            (collection_id, priority, exclude_id),
        )
        return row["priority"] if row else None

    def get_all_priorities(self, collection_id: int) -> list[tuple[int, str]]:
        rows = self.db.fetch_all(
            "SELECT id, priority FROM nodes WHERE collection_id = ? ORDER BY priority",
            (collection_id,),
        )
        return [(row["id"], row["priority"]) for row in rows]

    def get_tail_key(self, collection_id: int) -> Optional[str]:
        """Get the last priority in the collection"""
        row = self.db.fetch_one(
            "SELECT MAX(priority) FROM nodes WHERE collection_id = ?",
            (collection_id,),
        )
        return row[0] if row and row[0] is not None else None

    def get_neighbor_keys(
        self,
        collection_id: int,
        before_id: int | None,
        after_id: int | None,
    ) -> tuple[Optional[str], Optional[str]]:
        """Get priorities of nodes before and after for insertion"""
        a_key = None
        b_key = None
        if before_id is not None:
            row = self.db.fetch_one(
                "SELECT priority FROM nodes WHERE id = ? AND collection_id = ?",
                (before_id, collection_id),
            )
            if row is None:
                raise ValueError(f"Node {before_id} not found in collection {collection_id}")
            a_key = row["priority"]
        if after_id is not None:
            row = self.db.fetch_one(
                "SELECT priority FROM nodes WHERE id = ? AND collection_id = ?",
                (after_id, collection_id),
            )
            if row is None:
                raise ValueError(f"Node {after_id} not found in collection {collection_id}")
            b_key = row["priority"]
        return a_key, b_key

    def get_nodes_after(
        self,
        collection_id: int,
        priority: Optional[str],
        limit: int,
    ) -> list[Node]:
        """Get nodes after a given priority, ordered by priority"""
        if priority is None:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? ORDER BY priority LIMIT ?",
                (collection_id, limit),
            )
        else:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? AND priority > ? ORDER BY priority LIMIT ?",
                (collection_id, priority, limit),
            )
        return [self._row_to_model(r) for r in rows]
    
    def get_due(self, collection_id: int, now_ms: Optional[int] = None) -> list[Node]:
        now_ms = now_ms or int(time.time() * 1000)
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? AND due <= ? ORDER BY due",
            (collection_id, now_ms),
        )
        return [self._row_to_model(r) for r in rows]

    
