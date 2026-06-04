from src.models.user import User
from src.models.collection import Collection
from src.models.node import Node
from src.models.review import Review

class ImportExportRepository:
    def __init__(self, db):
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
