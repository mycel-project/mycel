import time
from typing import Optional

from src.db import Db
from src.models.review import Review



class ReviewRepository:
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Review:
        return Review(
            id=row["id"],
            node_id=row["node_id"],
            time=row["time"],
            duration=row["duration"],
            rating=row["rating"],
        )

    def create(
        self,
        node_id: int,
        rating: int,
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
            rating=rating,
        )
        self.db.execute(
            """INSERT INTO reviews
               (id, node_id, time, duration, rating)
               VALUES (?,?,?,?,?)""",
            (
                review.id,
                review.node_id,
                review.time,
                review.duration,
                review.rating,
            ),
        )
        return review

    def get_by_node(self, node_id: int) -> list[Review]:
        rows = self.db.fetch_all(
            "SELECT * FROM reviews WHERE node_id = ? ORDER BY time",
            (node_id,),
        )
        return [self._row_to_model(r) for r in rows]

    def delete(self, review_id: int) -> None:
        self.db.execute(
            "DELETE FROM reviews WHERE id = ?",
            (review_id,),
        )
