from typing import Optional
from src.core.review_context import ReviewContext
from src.db import Db
from src.models.review import Review
from src.repositories.review_repository import ReviewRepository
from src.core.scheduling_engine import SchedulingEngine
from src.schemas.node_update import NodeUpdate
from src.services.fsrs_service import FsrsService
from .node_service import NodeService
from src.utils.time import datetime_to_ms, end_of_day_ms, now_ms, start_of_day_ms

class ReviewService:
    # No caching at the moment
    def __init__(self, db: Db, scheduling_engine: SchedulingEngine, fsrs_service: FsrsService, node_service: NodeService):
        self._repo = ReviewRepository(db)
        self._fsrs_service = fsrs_service
        self._node_service = node_service
        self._scheduling_engine = scheduling_engine

    def review(
            self,
            col_id: int,
            node_id: int,
            rating: int,
            duration: int,
    ) -> None:
        card, review_log = self._fsrs_service.review_node(col_id, node_id, rating, duration)

        now = int(review_log.review_datetime.timestamp() * 1000)
        self._repo.create(
            node_id=node_id,
            rating=rating,
            duration=duration,
            now=now
        )
        self._node_service.update(node_id, NodeUpdate(
            stability=card.stability,
            difficulty=card.difficulty,
            state=int(card.state.value), 
            step=card.step,
            due=datetime_to_ms(card.due),
            last_review=now
        ))

    def get_reviews_for_today(self) -> list[Review]:
        now = now_ms()
        today_start = start_of_day_ms(now)
        today_end = end_of_day_ms(now)
        return self._repo.get_by_period(today_start, today_end)

    def get_next_review(self, col_id: int) -> Optional[int]:
        nodes = self._node_service.get_nodes_scheduling_context(col_id)
        today_reviews = self.get_reviews_for_today()
        today_reviews_context = []

        for r in today_reviews:
            node = self._node_service.get_node(r.node_id)

            if not node or node.type:
                continue

            today_reviews_context.append(
                ReviewContext(
                    id=r.id,
                    node_type=node.type,
                )
            )
                                
        return self._scheduling_engine.get_next_card(nodes, today_reviews_context)
