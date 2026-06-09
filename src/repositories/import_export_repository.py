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

        learning_units_rows = self.db.fetch_all(
            """
            SELECT lu.* FROM learning_units lu
            JOIN nodes n ON lu.node_id = n.id
            JOIN collections c ON n.collection_id = c.id
            WHERE c.user_id = :user_id
            """,
            {"user_id": user_id}
        )

        reviews_rows = self.db.fetch_all(
            """
            SELECT r.* FROM reviews r
            JOIN learning_units lu ON r.learning_unit_id = lu.id
            JOIN nodes n ON lu.node_id = n.id
            JOIN collections c ON n.collection_id = c.id
            WHERE c.user_id = :user_id
            """, 
            {"user_id": user_id}
        )

        return {
            "user": User.model_validate(user_row) if user_row else None,
            "collections": [Collection.model_validate(c) for c in collections_rows],
            "nodes": [Node.model_validate(n) for n in nodes_rows],
            "learning_units": [dict(lu) for lu in learning_units_rows],
            "reviews": [Review.model_validate(r) for r in reviews_rows]
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
                    """INSERT INTO nodes (id, collection_id, parent_id, base_for, template_id, created_at, updated_at, deleted_at, fields, data, status)
                       VALUES (:id, :collection_id, :parent_id, :base_for, :template_id, :created_at, :updated_at, :deleted_at, :fields, :data, :status)""",
                    {
                        "id": node.id, 
                        "collection_id": node.collection_id,
                        "parent_id": node.parent_id,
                        "base_for": node.base_for,
                        "template_id": node.template_id,
                        "created_at": node.created_at,
                        "updated_at": node.updated_at,
                        "deleted_at": node.deleted_at,
                        "fields": node.fields.model_dump_json(),
                        "data": node.data.model_dump_json(),
                        "status": node.status,
                    }
                ))

            for lu in col.learning_units:
                statements.append((
                    """INSERT INTO learning_units (id, node_id, unit_type, slot, position, due, last_review, unit_data)
                       VALUES (:id, :node_id, :unit_type, :slot, :position, :due, :last_review, :unit_data)""",
                    {
                        "id": lu.id,
                        "node_id": lu.node_id,
                        "unit_type": lu.type,
                        "slot": getattr(lu, 'slot', 0),
                        "position": lu.position,
                        "due": lu.due,
                        "last_review": lu.last_review,
                        "unit_data": lu.model_dump_json(exclude={"id", "node_id", "position", "due", "last_review", "type"}),
                    }
                ))

            for review in col.reviews:
                statements.append((
                    """INSERT INTO reviews (id, learning_unit_id, reviewed_at, duration, type_review_data, type, state_before)
                       VALUES (:id, :learning_unit_id, :reviewed_at, :duration, :type_review_data, :type, :state_before)""",
                    {
                        "id": review.id, 
                        "learning_unit_id": review.learning_unit_id,
                        "reviewed_at": review.reviewed_at,
                        "duration": review.duration, 
                        "type_review_data": review.type_review_data.model_dump_json(),
                        "type": review.type, 
                        "state_before": review.state_before.model_dump_json() if review.state_before else None
                    }
                ))

        self.db.execute_transaction(statements)
