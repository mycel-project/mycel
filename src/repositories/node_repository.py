import time
from typing import Optional

from src.db import Db
from src.models.node import Node, NodeFields, NodeStatus, NodeType
from src.models.node_data import NodeData

class NodeRepository:
    def __init__(self, db: Db):
        self.db = db
        self.collation = "" if self.db.is_sqlite else 'COLLATE "C"'

    # BASIC CRUD
        
    def create(
            self,
            collection_id: str,
            template_id: str,
            base_for: NodeType,
            fields: NodeFields,
            data: Optional[NodeData] = None,
            status: NodeStatus = NodeStatus.ACTIVE,
            parent_id: Optional[str] = None,
        ) -> Node:
            node = Node(
                collection_id=collection_id,
                template_id=template_id,
                base_for=base_for,
                fields=fields,
                data=data or NodeData(),
                status=status,
                parent_id=parent_id,
            )

            self.db.execute(
                """INSERT INTO nodes (id, collection_id, template_id, parent_id, base_for, fields, data, status, created_at, updated_at, deleted_at)
                   VALUES (:id, :collection_id, :template_id, :parent_id, :base_for, :fields, :data, :status, :created_at, :updated_at, :deleted_at)""",
                {
                    "id": node.id,
                    "collection_id": node.collection_id,
                    "template_id": node.template_id,
                    "parent_id": node.parent_id,
                    "base_for": node.base_for.value,  
                    "fields": node.fields.model_dump_json(),
                    "data": node.data.model_dump_json(),
                    "status": node.status.value,     
                    "created_at": node.created_at,
                    "updated_at": node.updated_at,
                    "deleted_at": node.deleted_at,
                },
            )
            return node

    def get(self, id: str) -> Optional[Node]:
        row = self.db.fetch_one("SELECT * FROM nodes WHERE id = :id", {"id": id})
        return Node.model_validate(row) if row else None

    def update(self, node: Node) -> None:
        node.updated_at = int(time.time() * 1000)
        
        self.db.execute(
            """UPDATE nodes 
               SET template_id = :template_id,
                   parent_id = :parent_id, 
                   base_for = :base_for, 
                   fields = :fields,
                   data = :data, 
                   status = :status,
                   updated_at = :updated_at, 
                   deleted_at = :deleted_at 
               WHERE id = :id""",
            {
                "id": node.id,
                "template_id": node.template_id,
                "parent_id": node.parent_id,
                "base_for": node.base_for.value,
                "fields": node.fields.model_dump_json(), 
                "data": node.data.model_dump_json(),
                "status": node.status.value,
                "updated_at": node.updated_at,
                "deleted_at": node.deleted_at,
            },
        )
        
    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM nodes WHERE id = :id", {"id": id})

    # DOMAIN

    def get_owned(self, user_id: str, col_id: str, node_id: str) -> Optional[Node]:
        row = self.db.fetch_one(
            """SELECT n.* FROM nodes n
               JOIN collections c ON n.collection_id = c.id
               WHERE n.id = :node_id AND n.collection_id = :col_id AND c.user_id = :user_id""",
            {"node_id": node_id, "col_id": col_id, "user_id": user_id},
        )
        return Node.model_validate(row) if row else None

    def get_by_collection(self, collection_id: str, limit: Optional[int] = None) -> list[Node]:
        if limit:
            rows = self.db.fetch_all(
                f"""
                SELECT n.* FROM nodes n
                JOIN collections c ON n.collection_id = c.id
                WHERE n.collection_id = :col_id 
                ORDER BY n.position {self.collation}
                LIMIT :limit
                """,
                {"col_id": collection_id, "limit": limit},
            )
        else:
            rows = self.db.fetch_all(
                f"""
                SELECT n.* FROM nodes n
                JOIN collections c ON n.collection_id = c.id
                WHERE n.collection_id = :col_id 
                ORDER BY n.position {self.collation}
                """,
                {"col_id": collection_id},
            )
        return [Node.model_validate(r) for r in rows]

    def get_by_type(self, collection_id: str, type: int) -> list[Node]:
        rows = self.db.fetch_all(
            f"""
            SELECT * FROM nodes WHERE collection_id = :col_id AND type = :type ORDER BY position {self.collation}
            """,
            {"col_id": collection_id, "type": type},
        )
        return [Node.model_validate(r) for r in rows]

    def get_children(self, node_id: str) -> list[Node]:
        rows = self.db.fetch_all(
            f"SELECT * FROM nodes WHERE parent_id = :node_id ORDER BY position {self.collation}",
            {"node_id": node_id},
        )
        return [Node.model_validate(r) for r in rows]

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
        return [Node.model_validate(r) for r in rows]

    def get_expired_deleted(self, collection_id: str, cutoff_ms: int) -> list[Node]:
        rows = self.db.fetch_all(
            """SELECT * FROM nodes WHERE collection_id = :col_id
               AND deleted_at IS NOT NULL AND deleted_at < :cutoff""",
            {"col_id": collection_id, "cutoff": cutoff_ms},
        )
        return [Node.model_validate(r) for r in rows]
