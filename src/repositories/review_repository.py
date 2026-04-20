import time
from typing import Optional

from src.db import Db
from src.models.review import TYPE_REVIEW_DATA_MAP, Review
from src.models.type_review_data import TypeReviewData
from src.types.node_type import NodeType



class ReviewRepository:
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Review:
        return Review(
            id=row["id"],
            node_id=row["node_id"],
            time=row["time"],
            duration=row["duration"],
            type_review_data=row["type_review_data"],
            type=row["type"],
        )

    def create(
        self,
        node_id: int,
        type: NodeType,
        type_review_data: Optional[TypeReviewData] = None,
        duration: int | None = None,
        now: int | None = None
    ) -> Review:
        if not now:
            now = int(time.time() * 1000)
        review = Review(
            id=now,
            node_id=node_id,
            time=now,
            duration=duration,
            type=type,
            type_review_data=type_review_data or TYPE_REVIEW_DATA_MAP[type]()
        )
        self.db.execute(
            """INSERT INTO reviews
               (id, node_id, time, duration, type_review_data, type)
               VALUES (?,?,?,?,?,?)""",
            (
                review.id,
                review.node_id,
                review.time,
                review.duration,
                review.type_review_data.model_dump_json(),
                review.type
            ),
        )
        return review

    def get_by_node(self, node_id: int) -> list[Review]:
        rows = self.db.fetch_all(
            "SELECT * FROM reviews WHERE node_id = ? ORDER BY time",
            (node_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def get_by_period(self, start: int, end: int) -> list[Review]:
        rows = self.db.fetch_all(
            """
            SELECT * FROM reviews
            WHERE time >= ? AND time < ?
            ORDER BY time
            """,
            (start, end),
        )
        return [self._row_to_model(r) for r in rows]

    def delete(self, review_id: int) -> None:
        self.db.execute(
            "DELETE FROM reviews WHERE id = ?",
            (review_id,),
        )

    def get_encounter_count(self, node_id: int) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM reviews WHERE node_id = ?",
            (node_id,),
        )
        return row["count"] if row else 0
