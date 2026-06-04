from src.db.models import CollectionORM, NodeORM, ReviewORM, UserORM
from src.models.user import User
from src.models.collection import Collection
from src.models.node import Node
from src.models.review import Review

class ExportRepository:
    def __init__(self, db_session):
        self.db = db_session

    def get_full_user_data(self, user_id: str) -> dict:
        user_orm = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        
        collections_orm = self.db.query(CollectionORM).filter(CollectionORM.user_id == user_id).all()
        
        nodes_orm = self.db.query(NodeORM).join(
            CollectionORM, NodeORM.collection_id == CollectionORM.id
        ).filter(CollectionORM.user_id == user_id).all()
        
        reviews_orm = self.db.query(ReviewORM).join(
            NodeORM, ReviewORM.node_id == NodeORM.id
        ).join(
            CollectionORM, NodeORM.collection_id == CollectionORM.id
        ).filter(CollectionORM.user_id == user_id).all()

        return {
            "user": User.from_db(user_orm) if user_orm else None,
            "collections": [Collection.from_db(c) for c in collections_orm],
            "nodes": [Node.from_db(n) for n in nodes_orm],
            "reviews": [Review.from_db(r) for r in reviews_orm]
        }
