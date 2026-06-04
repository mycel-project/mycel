import json

from src.db import Db
from src.models.export import FullExport
from src.models.user import User
from src.models.collection import Collection
from src.models.node import Node
from src.models.review import Review

class ImportExportRepository:
    def __init__(self, db: Db):
        self.db = db

    def get_full_user_data(self, user_id: str) -> dict:
            user_row = self.db.fetch_one(
                "SELECT * FROM users WHERE id = :user_id", 
                {"user_id": user_id}
            )

            collections_rows = self.db.fetch_all(
                "SELECT * FROM collections WHERE user_id = :user_id", 
                {"user_id": user_id}
            )

            nodes_rows = self.db.fetch_all(
                """
                SELECT n.* FROM nodes n
                JOIN collections c ON n.collection_id = c.id
                WHERE c.user_id = :user_id
                """, 
                {"user_id": user_id}
            )

            reviews_rows = self.db.fetch_all(
                """
                SELECT r.* FROM reviews r
                JOIN nodes n ON r.node_id = n.id
                JOIN collections c ON n.collection_id = c.id
                WHERE c.user_id = :user_id
                """, 
                {"user_id": user_id}
            )

            return {
                "user": User.from_db(user_row) if user_row else None,
                "collections": [Collection.from_db(c) for c in collections_rows],
                "nodes": [Node.from_db(n) for n in nodes_rows],
                "reviews": [Review.from_db(r) for r in reviews_rows]
            }

    def import_full_user_data(self, data: FullExport) -> None:
        statements = []

        target_user_id = data.user.id

        if data.user:
            statements.append((
                "UPDATE users SET name = :name, conf = :conf WHERE id = :id",
                {"name": data.user.name, "conf": data.user.conf.model_dump_json(), "id": target_user_id}
            ))

        for col in data.collections:
            statements.append((
                """INSERT INTO collections (id, user_id, name, created_at, updated_at, conf, algoconf)
                   VALUES (:id, :user_id, :name, :created_at, :updated_at, :conf, :algoconf)""",
                {
                    "id": col.id, 
                    "user_id": target_user_id, 
                    "name": col.name,
                    "created_at": col.created_at, 
                    "updated_at": col.updated_at,
                    "conf": col.conf.model_dump_json(), 
                    "algoconf": col.algoconf.model_dump_json()
                }
            ))

            for node in col.nodes:
                statements.append((
                    """INSERT INTO nodes (id, collection_id, parent_id, type, created_at, updated_at, deleted_at, data, type_data, due, content, position, last_review)
                       VALUES (:id, :collection_id, :parent_id, :type, :created_at, :updated_at, :deleted_at, :data, :type_data, :due, :content, :position, :last_review)""",
                    {
                        "id": node.id, 
                        "collection_id": node.collection_id,
                        "parent_id": node.parent_id,
                        "type": node.type, "created_at": node.created_at, "updated_at": node.updated_at,
                        "deleted_at": node.deleted_at, "data": node.data.to_db(),
                        "type_data": node.type_data if isinstance(node.type_data, str) else (
                            node.type_data.model_dump_json() if hasattr(node.type_data, "model_dump_json") else json.dumps(node.type_data)
                        ), 
                        "due": node.due, "content": node.content.to_db(), 
                        "position": node.position, "last_review": node.last_review
                    }
                ))

            for review in col.reviews:
                statements.append((
                    """INSERT INTO reviews (id, node_id, time, duration, type_review_data, type, node_state_before)
                       VALUES (:id, :node_id, :time, :duration, :type_review_data, :type, :node_state_before)""",
                    {
                        "id": review.id, 
                        "node_id": review.node_id,
                        "time": review.time,
                        "duration": review.duration, 
                        "type_review_data": review.type_review_data if isinstance(review.type_review_data, str) else (
                            review.type_review_data.model_dump_json() if hasattr(review.type_review_data, "model_dump_json") else json.dumps(review.type_review_data)
                        ),
                        "type": review.type, 
                        "node_state_before": review.node_state_before.model_dump_json() if review.node_state_before else None
                    }
                ))
        self.db.execute_transaction(statements)
