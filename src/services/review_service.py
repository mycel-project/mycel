from typing import Optional, cast
from src.core.node_scheduling_context import NodeSchedulingContext
from src.core.review_context import ReviewContext
from src.db import Db
from src.domain.domain_exceptions import NoReviewToUndo, NotAFragment, NotASpore, ReviewUndoNotAllowedError
from src.models.node_state_before import NodeStateBefore
from src.models.review import Review
from src.models.type_data.fragment_data import FragmentData
from src.models.type_data.spore_data import SporeData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.repositories.review_repository import ReviewRepository
from src.core.scheduling_engine import SchedulingEngine
from src.schemas.node_update import NodeUpdate
from src.services.cache.pending_review_cache import PendingReviewCache
from src.services.fsrs_service import FsrsService
from src.types.node_type import NodeType
from .node_service import NodeService
from src.utils.time import add_days_ms, datetime_to_ms, end_of_day_ms, ms_to_datetime, now_ms, now_s, start_of_day_ms
from src.models.node import Node

class ReviewService:
    # No caching at the moment
    """
    No date/datetime object
    """
    def __init__(self, db: Db, scheduling_engine: SchedulingEngine, fsrs_service: FsrsService, node_service: NodeService, pending_review_cache: PendingReviewCache):
        self._repo = ReviewRepository(db)
        self._fsrs_service = fsrs_service
        self._node_service = node_service
        self._scheduling_engine = scheduling_engine
        self._pending_review_cache = pending_review_cache

    def _build_node_state_before(self, node: Node) -> NodeStateBefore:
        return NodeStateBefore(
            due=node.due,
            last_review=node.last_review,
            type_data=node.type_data,
        )

    def review_spore(
            self,
            col_id: int,
            node_id: int,
            duration: int,
            data: SporeReviewData,
    ) -> Node:
        node = self._node_service.get_node(node_id)
        if not node.type == NodeType.SPORE:
            raise NotASpore(node_id)
        card, review_log = self._fsrs_service.review_node(col_id, node_id, data.rating, duration)
        now = int(review_log.review_datetime.timestamp() * 1000)
        type_data = SporeData(
            stability=card.stability,
            difficulty=card.difficulty,
            state=int(card.state.value),
            step=card.step,
        )
        node_state_before = self._build_node_state_before(node)
        self._repo.create(
            node_id=node_id,
            type=node.type,
            type_review_data=data,
            duration=duration,
            now=now,
            node_state_before=node_state_before
        )
        return self._node_service.update(
            node_id,
            NodeUpdate(
                type_data=type_data,
                due=datetime_to_ms(card.due),
                last_review=now
            )
        )

    def review_fragment(
            self,
            col_id: int,
            node_id: int,
            duration: int,
            data: FragmentReviewData,
    ) -> Node:
        node = self._node_service.get_node(node_id)
        if not node.type == NodeType.FRAGMENT:
            raise NotAFragment(node_id)
        encounter_count = self.get_encounter_count(node_id)
        context = NodeSchedulingContext(
            id=node.id,
            type=node.type,
            encounter_count=encounter_count,
            due=node.due,
        )
        next_interval = self._scheduling_engine.next_linear_interval(context)
        now = now_ms()
        node_state_before = self._build_node_state_before(node)
        self._repo.create(
            node_id=node_id,
            type=node.type,
            type_review_data=data,
            duration=duration,
            now=now,
            node_state_before=node_state_before
        )
        return self._node_service.update(
            node.id,
            NodeUpdate(
                type_data=FragmentData(),
                due=add_days_ms(now, next_interval),
                last_review=now
            )
        )

    def get_encounter_count(self, node_id: int) -> int:
        return self._repo.get_encounter_count(node_id)
    
    def get_reviews_for_today(self) -> list[Review]:
        now = now_ms()
        today_start = start_of_day_ms(now)
        today_end = end_of_day_ms(now)
        return self._repo.get_by_period(today_start, today_end)

    def get_next_review_id(self, col_id: int) -> int | None:
        nodes = self._node_service.get_nodes_scheduling_context(col_id)
        today_reviews = self.get_reviews_for_today()
        today_reviews_context = []

        for r in today_reviews:
            node = self._node_service.get_node(r.node_id, True)

            if not node:
                continue

            today_reviews_context.append(
                ReviewContext(
                    id=r.id,
                    node_type=node.type,
                )
            )
                                
        return self._scheduling_engine.get_next_node(nodes, today_reviews_context)

    def get_next_review(self, col_id: int) -> Node | None:
        next_node_id = self.get_next_review_id(col_id)
        if not next_node_id:
            return None
        node = self._node_service.get_node(next_node_id)
        self._pending_review_cache.set(next_node_id)
        return node

    def set_pending_node_id(self, node_id: int):
        self._pending_review_cache.set(node_id)

    def get_pending_node_id(self) -> int | None: 
        return self._pending_review_cache.get()

    def undo_review(self, col_id: int, max_age_min: int | None = None) -> Review:
        last_review = self._repo.get_last_review_by_collection(col_id)

        if last_review is None:
            raise NoReviewToUndo()

        if max_age_min is not None:
            age = now_s() - (last_review.time // 1000)
            max_age_s = max_age_min * 60
            if age > max_age_s:
                raise ReviewUndoNotAllowedError(age, max_age_s)

        self._repo.delete(last_review.id)
        
        return last_review
