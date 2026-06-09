import time
from typing import Optional
from uuid import uuid4
from src.db import Db
from src.models.learning_unit import LearningUnit
from src.models.node import NodeType
from src.models.review import Review
from src.models.type_review_data import TypeReviewData

class ReviewRepository:
    def __init__(self, db: Db):
        self.db = db

    def create(self, learning_unit_id: str, type: NodeType, state_before: LearningUnit, type_review_data: TypeReviewData, duration: int | None = None) -> Review:
        now = int(time.time() * 1000)
        review_id = str(uuid4())
        review = Review(
            id=review_id, learning_unit_id=learning_unit_id, reviewed_at=now, duration=duration, type=type,
            type_review_data=type_review_data,
            state_before=state_before,
        )
        self.db.execute(
            """INSERT INTO reviews (id, learning_unit_id, reviewed_at, duration, type_review_data, type, state_before)
               VALUES (:id, :learning_unit_id, :reviewed_at, :duration, :type_review_data, :type, :state_before)""",
            {
                "id": review.id, "learning_unit_id": review.learning_unit_id, "reviewed_at": review.reviewed_at,
                "duration": review.duration, "type_review_data": review.type_review_data.model_dump_json(),
                "type": review.type, "state_before": review.state_before.model_dump_json() if review.state_before else None,
            },
        )
        return review

    def get_by_node(self, learning_unit_id: str) -> list[Review]:
        rows = self.db.fetch_all("SELECT * FROM reviews WHERE learning_unit_id = :learning_unit_id ORDER BY reviewed_at", {"learning_unit_id": learning_unit_id})
        return [Review.model_validate(r) for r in rows]

    def get_by_period(self, start: int, end: int, col_id: str) -> list[Review]:
        rows = self.db.fetch_all(
            """SELECT r.* FROM reviews r
               JOIN learning_units lu ON r.learning_unit_id = lu.id
               JOIN nodes n ON lu.node_id = n.id
               WHERE r.reviewed_at >= :start AND r.reviewed_at < :end AND n.collection_id = :col_id
               ORDER BY r.reviewed_at""",
            {"start": start, "end": end, "col_id": col_id},
        )
        return [Review.model_validate(r) for r in rows]

    def delete(self, review_id: str) -> None:
        self.db.execute("DELETE FROM reviews WHERE id = :id", {"id": review_id})

    def get_encounter_count(self, learning_unit_id: str) -> int:
        row = self.db.fetch_one("SELECT COUNT(*) as count FROM reviews WHERE learning_unit_id = :learning_unit_id", {"learning_unit_id": learning_unit_id})
        return row["count"] if row else 0

    def get_last_review_by_collection(self, col_id: str) -> Optional[Review]:
        row = self.db.fetch_one(
            """SELECT r.* FROM reviews r
               JOIN learning_units lu ON r.learning_unit_id = lu.id
               JOIN nodes n ON lu.node_id = n.id
               WHERE n.collection_id = :col_id
               ORDER BY r.reviewed_at DESC LIMIT 1""",
            {"col_id": col_id},
        )
        return Review.model_validate(row) if row else None
