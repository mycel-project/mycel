import json
import time
from typing import Optional
from uuid import uuid4
from src.db import Db
from src.models.node_state_before import NodeStateBefore
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
            node_state_before=(
                NodeStateBefore.from_dict(
                    json.loads(row["node_state_before"]),
                    NodeType(row["type"])
                )
            ),
        )

    def create(self, node_id: str, type: NodeType, node_state_before: NodeStateBefore, type_review_data: Optional[TypeReviewData] = None, duration: int | None = None, now: int | None = None) -> Review:
        if not now:
            now = int(time.time() * 1000)
        review_id = str(uuid4())
        review = Review(
            id=review_id, node_id=node_id, time=now, duration=duration, type=type,
            type_review_data=type_review_data or TYPE_REVIEW_DATA_MAP[type](),
            node_state_before=node_state_before,
        )
        self.db.execute(
            """INSERT INTO reviews (id, node_id, time, duration, type_review_data, type, node_state_before)
               VALUES (:id, :node_id, :time, :duration, :type_review_data, :type, :node_state_before)""",
            {
                "id": review.id, "node_id": review.node_id, "time": review.time,
                "duration": review.duration, "type_review_data": review.type_review_data.model_dump_json(),
                "type": review.type, "node_state_before": review.node_state_before.model_dump_json() if review.node_state_before else None,
            },
        )
        return review

    def get_by_node(self, node_id: str) -> list[Review]:
        rows = self.db.fetch_all("SELECT * FROM reviews WHERE node_id = :node_id ORDER BY time", {"node_id": node_id})
        return [self._row_to_model(r) for r in rows]

    def get_by_period(self, start: int, end: int, col_id: str) -> list[Review]:
        rows = self.db.fetch_all(
            """SELECT r.* FROM reviews r
               JOIN nodes n ON r.node_id = n.id
               WHERE r.time >= :start AND r.time < :end AND n.collection_id = :col_id
               ORDER BY r.time""",
            {"start": start, "end": end, "col_id": col_id},
        )
        return [self._row_to_model(r) for r in rows]

    def delete(self, review_id: str) -> None:
        self.db.execute("DELETE FROM reviews WHERE id = :id", {"id": review_id})

    def get_encounter_count(self, node_id: str) -> int:
        row = self.db.fetch_one("SELECT COUNT(*) as count FROM reviews WHERE node_id = :node_id", {"node_id": node_id})
        return row["count"] if row else 0

    def get_last_review_by_collection(self, col_id: str) -> Optional[Review]:
        row = self.db.fetch_one(
            """SELECT r.* FROM reviews r
               JOIN nodes n ON n.id = r.node_id
               WHERE n.collection_id = :col_id
               ORDER BY r.time DESC LIMIT 1""",
            {"col_id": col_id},
        )
        return self._row_to_model(row) if row else None
