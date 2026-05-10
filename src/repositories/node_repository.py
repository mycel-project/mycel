import json
import time
from typing import Optional

from src.db import Db
from src.models.node import TYPE_DATA_MAP, Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.type_data import TypeData
from src.types.node_type import NodeType

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
            deleted_at=row["deleted_at"],
            data=NodeData.from_db(row["data"]),
            due=row["due"],
            content=NodeContent.from_db(row["content"]),
            last_review=row["last_review"], 
            type_data=row["type_data"],
            position=row["position"],
    )

    def create(
        self,
        collection_id: int,
        content: NodeContent,
        data: Optional[NodeData],
        type: NodeType,
        position: str,        
        type_data: Optional[TypeData] = None,
        parent_id: Optional[int] = None,
    ) -> Node:
        now = int(time.time() * 1000)
        node = Node(
            id=now,
            collection_id=collection_id,
            parent_id=parent_id,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            data=data or NodeData(),
            type_data=type_data or TYPE_DATA_MAP[type](),
            due=now,
            content=content, 
            position=position,
            type=type
        )
        self.db.execute(
            """INSERT INTO nodes
               (id, collection_id, parent_id, type, created_at, updated_at, deleted_at, data, type_data, due, content, position)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                node.id,
                node.collection_id,
                node.parent_id,
                node.type,
                node.created_at,
                node.updated_at,
                node.deleted_at,
                node.data.to_db(),
                node.type_data.model_dump_json(),
                node.due,
                node.content.to_db(),  
                node.position,
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
               parent_id=?, type=?, due=?, content=?, 
               last_review=?, type_data=?, position=?, updated_at=?, data=?, deleted_at=?
               WHERE id=?""",
            (
                node.parent_id,
                node.type,
                node.due,
                node.content.to_db(), 
                node.last_review,
                node.type_data.model_dump_json(),
                node.position,
                now,
                node.data.to_db(),
                node.deleted_at,
                node.id,
            ),
        )

    def delete(self, id: int) -> None:
        self.db.execute("DELETE FROM nodes WHERE id = ?", (id,))

    def get_by_collection(self, collection_id: int, limit: Optional[int] = None) -> list[Node]:
        if limit:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? ORDER BY position LIMIT ?",
                (collection_id, limit),
            )
        else:
            rows = self.db.fetch_all(
                "SELECT * FROM nodes WHERE collection_id = ? ORDER BY position",
                (collection_id,),
            )
        return [self._row_to_model(r) for r in rows]

    def get_by_type(self, collection_id: int, type: int) -> list[Node]:
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? AND type = ? ORDER BY position",
            (collection_id, type),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_state(self, collection_id: int, state: int) -> list[Node]:
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? AND state = ? ORDER BY position",
            (collection_id, state),
        )
        return [self._row_to_model(r) for r in rows]

    def update_position(self, node_id: int, position: str) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET position = ?, updated_at = ? WHERE id = ?",
            (position, now, node_id),
        )

    def update_state(self, node_id: int, state: int) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET state = ?, updated_at = ? WHERE id = ?",
            (state, now, node_id),
        )

    def update_last_review(self, node_id: int) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET last_review = ?, updated_at = ? WHERE id = ?",
            (now, now, node_id),
        )
    
    def get_due(self, collection_id: int, now_ms: Optional[int] = None) -> list[Node]:
        now_ms = now_ms or int(time.time() * 1000)
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = ? AND due <= ? ORDER BY due",
            (collection_id, now_ms),
        )
        return [self._row_to_model(r) for r in rows]

    def get_children(self, node_id: int) -> list[Node]:
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE parent_id = ? ORDER BY position",
            (node_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_children_recursive(self, node_id: int) -> list[Node]:
        """
        Does not include root node
        """
        rows = self.db.fetch_all(
            """
            WITH RECURSIVE subtree AS (
                SELECT * FROM nodes WHERE parent_id = ? 
                UNION ALL
                SELECT n.*
                FROM nodes n
                INNER JOIN subtree s ON n.parent_id = s.id
            )
            SELECT * FROM subtree
            """,
            (node_id,),
        )

        return [self._row_to_model(r) for r in rows]

    
    # Priorisation. Exclude soft deleted nodes.

    def get_position(self, node_id: int) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT position FROM nodes WHERE id = ?",
            (node_id,),
        )
        return row["position"] if row else None

    def get_all_positions(self, collection_id: int) -> list[tuple[int, str]]:
        rows = self.db.fetch_all(
            "SELECT id, position FROM nodes WHERE collection_id = ? AND deleted_at IS NULL ORDER BY position",
            (collection_id,),
        )
        return [(row["id"], row["position"]) for row in rows]

    def count_before_position(self, collection_id: int, position: str) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) FROM nodes WHERE collection_id = ? AND position < ? AND deleted_at IS NULL",
            (collection_id, position),
        )
        return row[0] if row else 0

    def count_by_collection(self, collection_id: int) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) FROM nodes WHERE collection_id = ? AND deleted_at IS NULL",
            (collection_id,),
        )
        return row[0] if row else 0

    def get_position_at_offset(self, collection_id: int, offset: int) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT position FROM nodes WHERE collection_id = ? AND deleted_at IS NULL ORDER BY position LIMIT 1 OFFSET ?",
            (collection_id, offset),
        )
        return row["position"] if row else None

    def get_predecessor_position(self, collection_id: int, position: str, exclude_id: int) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT position FROM nodes "
            "WHERE collection_id = ? AND position < ? AND id != ? AND deleted_at IS NULL "
            "ORDER BY position DESC LIMIT 1",
            (collection_id, position, exclude_id),
        )
        return row["position"] if row else None

    def get_successor_position(self, collection_id: int, position: str, exclude_id: int) -> Optional[str]:
        row = self.db.fetch_one(
            "SELECT position FROM nodes "
            "WHERE collection_id = ? AND position > ? AND id != ? AND deleted_at IS NULL "
            "ORDER BY position ASC LIMIT 1",
            (collection_id, position, exclude_id),
        )
        return row["position"] if row else None

    def get_tail_key(self, collection_id: int) -> Optional[str]:
        """Get the last position in the collection, ordered lexicographically."""
        row = self.db.fetch_one(
            "SELECT position FROM nodes WHERE collection_id = ? AND deleted_at IS NULL ORDER BY position DESC LIMIT 1",
            (collection_id,),
        )
        return row["position"] if row else None
