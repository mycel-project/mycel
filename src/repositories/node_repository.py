import time
from typing import Optional
from uuid import uuid4

from src.db import Db
from src.models.node import TYPE_DATA_MAP, Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.type_data import TypeData
from src.types.node_type import NodeType

class NodeRepository:
    def __init__(self, db: Db):
        self.db = db
        self.collation = "" if self.db.is_sqlite else 'COLLATE "C"'

    def create(self, collection_id: str, content: NodeContent, type: NodeType, position: str, data: Optional[NodeData] = None, due: Optional[int] = None, type_data: Optional[TypeData] = None, parent_id: Optional[str] = None) -> Node:
        now = int(time.time() * 1000)
        node_id = str(uuid4())
        node = Node(
            id=node_id, collection_id=collection_id, parent_id=parent_id,
            created_at=now, updated_at=now, deleted_at=None,
            data=data or NodeData(), type_data=type_data or TYPE_DATA_MAP[type](),
            due=due if due is not None else now, content=content, position=position, type=type
        )
        self.db.execute(
            """INSERT INTO nodes (id, collection_id, parent_id, type, created_at, updated_at, deleted_at, data, type_data, due, content, position)
               VALUES (:id, :collection_id, :parent_id, :type, :created_at, :updated_at, :deleted_at, :data, :type_data, :due, :content, :position)""",
            {
                "id": node.id, "collection_id": node.collection_id, "parent_id": node.parent_id,
                "type": node.type, "created_at": node.created_at, "updated_at": node.updated_at,
                "deleted_at": node.deleted_at, "data": node.data.to_db(),
                "type_data": node.type_data.model_dump_json(), "due": node.due,
                "content": node.content.to_db(), "position": node.position,
            },
        )
        return node

    def get(self, id: str) -> Optional[Node]:
        row = self.db.fetch_one("SELECT * FROM nodes WHERE id = :id", {"id": id})
        return Node.from_db(row) if row else None

    def update(self, node: Node) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            """UPDATE nodes SET parent_id=:parent_id, type=:type, due=:due, content=:content,
               last_review=:last_review, type_data=:type_data, position=:position,
               updated_at=:updated_at, data=:data, deleted_at=:deleted_at WHERE id=:id""",
            {
                "parent_id": node.parent_id, "type": node.type, "due": node.due,
                "content": node.content.to_db(), "last_review": node.last_review,
                "type_data": node.type_data.model_dump_json(), "position": node.position,
                "updated_at": now, "data": node.data.to_db(), "deleted_at": node.deleted_at,
                "id": node.id,
            },
        )

    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM nodes WHERE id = :id", {"id": id})

    def due_count_by_type_and_day(self, collection_id: str, start_ms: int, to_ms: int, tz_offset_minutes: int = 0) -> list[tuple[int, int, int]]:
        """
        day_start_ms is UTC midnight of the local day (i.e. local midnight expressed in UTC).
        e.g. for UTC+1, May 20 local → 2026-05-19 23:00:00 UTC.
        """
        tz_offset_ms = tz_offset_minutes * 60_000
        dismiss_filter = (
            "json_extract(type_data, '$.dismiss') = 1"
            if self.db.is_sqlite
            else "type_data::jsonb->>'dismiss' = 'true'"
        )
        rows = self.db.fetch_all(
            f"""
            SELECT
                (CAST((due + :tz) AS BIGINT) / 86400000) * 86400000 - :tz AS day_start_ms,
                type,
                COUNT(*) as count
            FROM nodes
            WHERE collection_id = :col_id
              AND due >= :start_ms
              AND due < :to_ms
              AND deleted_at IS NULL
              AND NOT (type = 1 AND {dismiss_filter})
            GROUP BY day_start_ms, type
            ORDER BY day_start_ms
            """,
            {"tz": tz_offset_ms, "col_id": collection_id, "start_ms": start_ms, "to_ms": to_ms},
        )
        return [(row["day_start_ms"], row["type"], row["count"]) for row in rows]

    def get_owned(self, user_id: str, col_id: str, node_id: str) -> Optional[Node]:
        row = self.db.fetch_one(
            """SELECT n.* FROM nodes n
               JOIN collections c ON n.collection_id = c.id
               WHERE n.id = :node_id AND n.collection_id = :col_id AND c.user_id = :user_id""",
            {"node_id": node_id, "col_id": col_id, "user_id": user_id},
        )
        return Node.from_db(row) if row else None

    def get_by_collection(self, user_id: str, collection_id: str, limit: Optional[int] = None) -> list[Node]:
        if limit:
            rows = self.db.fetch_all(
                f"""
                SELECT n.* FROM nodes n
                JOIN collections c ON n.collection_id = c.id
                WHERE n.collection_id = :col_id AND c.user_id = :user_id
                ORDER BY n.position {self.collation}
                LIMIT :limit
                """,
                {"col_id": collection_id, "user_id": user_id, "limit": limit},
            )
        else:
            rows = self.db.fetch_all(
                f"""
                SELECT n.* FROM nodes n
                JOIN collections c ON n.collection_id = c.id
                WHERE n.collection_id = :col_id AND c.user_id = :user_id
                ORDER BY n.position {self.collation}
                """,
                {"col_id": collection_id, "user_id": user_id},
            )
        return [Node.from_db(r) for r in rows]

    def get_by_type(self, collection_id: str, type: int) -> list[Node]:
        rows = self.db.fetch_all(
            f"""
            SELECT * FROM nodes WHERE collection_id = :col_id AND type = :type ORDER BY position {self.collation}
            """,
            {"col_id": collection_id, "type": type},
        )
        return [Node.from_db(r) for r in rows]

    def get_by_state(self, collection_id: str, state: int) -> list[Node]:
        rows = self.db.fetch_all(
            f"""SELECT * FROM nodes WHERE collection_id = :col_id AND state = :state ORDER BY position {self.collation}
            """,
            {"col_id": collection_id, "state": state},
        )
        return [Node.from_db(r) for r in rows]

    def update_position(self, node_id: str, position: str) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET position = :position, updated_at = :now WHERE id = :id",
            {"position": position, "now": now, "id": node_id},
        )

    def update_state(self, node_id: str, state: int) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET state = :state, updated_at = :now WHERE id = :id",
            {"state": state, "now": now, "id": node_id},
        )

    def update_last_review(self, node_id: str) -> None:
        now = int(time.time() * 1000)
        self.db.execute(
            "UPDATE nodes SET last_review = :now, updated_at = :now WHERE id = :id",
            {"now": now, "id": node_id},
        )

    def get_due(self, collection_id: str, now_ms: Optional[int] = None) -> list[Node]:
        now_ms = now_ms or int(time.time() * 1000)
        rows = self.db.fetch_all(
            "SELECT * FROM nodes WHERE collection_id = :col_id AND due <= :now_ms ORDER BY due",
            {"col_id": collection_id, "now_ms": now_ms},
        )
        return [Node.from_db(r) for r in rows]

    def get_children(self, node_id: str) -> list[Node]:
        rows = self.db.fetch_all(
            f"SELECT * FROM nodes WHERE parent_id = :node_id ORDER BY position {self.collation}",
            {"node_id": node_id},
        )
        return [Node.from_db(r) for r in rows]

    def get_children_recursive(self, node_id: str) -> list[Node]:
        """Does not include root node"""
        rows = self.db.fetch_all(
            """
            WITH RECURSIVE subtree AS (
                SELECT * FROM nodes WHERE parent_id = :node_id
                UNION ALL
                SELECT n.* FROM nodes n
                INNER JOIN subtree s ON n.parent_id = s.id
            )
            SELECT * FROM subtree
            """,
            {"node_id": node_id},
        )
        return [Node.from_db(r) for r in rows]

    def get_expired_deleted(self, collection_id: str, cutoff_ms: int) -> list[Node]:
        rows = self.db.fetch_all(
            """SELECT * FROM nodes WHERE collection_id = :col_id
               AND deleted_at IS NOT NULL AND deleted_at < :cutoff""",
            {"col_id": collection_id, "cutoff": cutoff_ms},
        )
        return [Node.from_db(r) for r in rows]

    def get_position(self, node_id: str) -> Optional[str]:
        row = self.db.fetch_one("SELECT position FROM nodes WHERE id = :id", {"id": node_id})
        return row["position"] if row else None

    def get_all_positions(self, collection_id: str) -> list[tuple[str, str]]:
        rows = self.db.fetch_all(
            f"SELECT id, position FROM nodes WHERE collection_id = :col_id AND deleted_at IS NULL ORDER BY position {self.collation}",
            {"col_id": collection_id},
        )
        return [(row["id"], row["position"]) for row in rows]

    def count_before_position(self, collection_id: str, position: str) -> int:
        row = self.db.fetch_one(
            f"SELECT COUNT(*) as count FROM nodes WHERE collection_id = :col_id AND position {self.collation} < :position AND deleted_at IS NULL",
            {"col_id": collection_id, "position": position},
        )
        return row["count"] if row else 0

    def count_by_collection(self, collection_id: str) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM nodes WHERE collection_id = :col_id AND deleted_at IS NULL",
            {"col_id": collection_id},
        )
        return row["count"] if row else 0

    def get_position_at_offset(self, collection_id: str, offset: int) -> Optional[str]:
        row = self.db.fetch_one(
            f"SELECT position FROM nodes WHERE collection_id = :col_id AND deleted_at IS NULL ORDER BY position {self.collation} LIMIT 1 OFFSET :offset",
            {"col_id": collection_id, "offset": offset},
        )
        return row["position"] if row else None

    def get_predecessor_position(self, collection_id: str, position: str, exclude_id: str) -> Optional[str]:
        row = self.db.fetch_one(
            f"""SELECT position FROM nodes
            WHERE collection_id = :col_id AND position {self.collation} < :position AND id != :exclude_id AND deleted_at IS NULL
            ORDER BY position {self.collation} DESC LIMIT 1""",
            {"col_id": collection_id, "position": position, "exclude_id": exclude_id},
        )
        return row["position"] if row else None

    def get_successor_position(self, collection_id: str, position: str, exclude_id: str) -> Optional[str]:
        row = self.db.fetch_one(
            f"""SELECT position FROM nodes
               WHERE collection_id = :col_id AND position {self.collation} > :position AND id != :exclude_id AND deleted_at IS NULL
               ORDER BY position {self.collation} ASC LIMIT 1""",
            {"col_id": collection_id, "position": position, "exclude_id": exclude_id},
        )
        return row["position"] if row else None

    def get_tail_key(self, collection_id: str) -> Optional[str]:
        """Get the last position in the collection, ordered lexicographically."""
        row = self.db.fetch_one(
            f"SELECT position FROM nodes WHERE collection_id = :col_id AND deleted_at IS NULL ORDER BY position {self.collation} DESC LIMIT 1",
            {"col_id": collection_id},
        )
        return row["position"] if row else None
