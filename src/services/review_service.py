from typing import Optional
from dataclasses import  asdict

from src.db import Db
from src.models.review import Review
from src.repositories.review_repository import ReviewRepository
from src.services.fsrs_service import FsrsService
from .node_service import NodeService
from src.utils.time import datetime_to_ms

class ReviewService:
    def __init__(self, db: Db, fsrs_service: FsrsService, node_service: NodeService):
        self._repo = ReviewRepository(db)
        self._fsrs_service = fsrs_service
        self._node_service = node_service

    def review(
            self,
            node_id: int,
            rating: int,
            duration: int,
    ) -> None:
        card, review_log = self._fsrs_service.review_node(node_id, rating, duration)

        now = int(review_log.review_datetime.timestamp() * 1000)
        self._repo.create(
            node_id=node_id,
            rating=rating,
            duration=duration,
            now=now
        )
        self._node_service.update(node_id, {
            "stability": card.stability,
            "difficulty": card.difficulty,
            "state": int(card.state.value), 
            "step": card.step,
            "due": datetime_to_ms(card.due),
            "last_review": now
        })
        
    def get_reviews(self, node_id: int) -> list[Review]:
        reviews = self._repo.get_by_node(node_id)
        return reviews
