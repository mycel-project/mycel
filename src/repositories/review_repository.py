import json

from src.db import Db
from src.models.review import Review


class ReviewRepository:
    def __init__(self, db: Db):
        self.db = db

    def _row_to_model(self, row) -> Review:
        return Review(
            id=row["id"],
            card_id=row["card_id"],
            review_time=row["review_time"],
            rating=row["rating"],
            review_type=row["review_type"],
            interval=row["interval"],
            ease=row["ease"],
            state_before=json.loads(row["state_before"]),
            state_after=json.loads(row["state_after"]),
        )

    def create(self, review: Review) -> Review:
        row_id = self.db.execute_returning(
            """INSERT INTO reviews
               (card_id, review_time, rating, review_type, interval, ease, state_before, state_after)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                review.card_id, review.review_time, review.rating, review.review_type,
                review.interval, review.ease,
                json.dumps(review.state_before), json.dumps(review.state_after),
            ),
        )
        review.id = row_id
        return review

    def get_by_card(self, card_id: int) -> list[Review]:
        rows = self.db.fetch_all(
            "SELECT * FROM reviews WHERE card_id = ? ORDER BY review_time",
            (card_id,),
        )
        return [self._row_to_model(r) for r in rows]
