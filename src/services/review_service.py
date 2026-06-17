from src.core.review_context import ReviewContext
from src.db import Db
from src.domain.domain_exceptions import NoReviewToUndo, ReviewUndoNotAllowedError
from src.models.learning_unit import LearningUnit
from src.models.review import Review
from src.models.spore import FsrsData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.repositories.review_repository import ReviewRepository
from src.core.scheduling_engine import SchedulingEngine
from src.schemas.learning_unit_update import FragmentUpdate, SporeUpdate
from src.services.fsrs_service import FsrsService
from .node_service import NodeService
from src.utils.time import MS_PER_DAY, datetime_to_ms, now_ms, now_s, start_of_local_day_ms, start_of_local_today_ms
from src.models.node import Node, NodeType

class ReviewService:
    # No caching at the moment
    """
    No date/datetime object
    """
    def __init__(self, db: Db, scheduling_engine: SchedulingEngine, fsrs_service: FsrsService, node_service: NodeService):
        self._repo = ReviewRepository(db)
        self._fsrs_service = fsrs_service
        self._node_service = node_service
        self._scheduling_engine = scheduling_engine

    def review_spore(
            self,
            user_id: str,
            col_id: str,
            spore_id: str,
            duration: int,
            data: SporeReviewData,
    ) -> Node:
        node = self._node_service.get_node_from_learning_unit(spore_id)
        spore = node.get_spore(spore_id)
        card, _ = self._fsrs_service.review(user_id, col_id, spore_id, data.rating, duration)
        now = now_ms()
        type_data = FsrsData(
            stability=card.stability,
            difficulty=card.difficulty,
            state=int(card.state.value),
            step=card.step,
        )
        self._repo.create(
            learning_unit_id=spore_id,
            type=NodeType.SPORE,
            type_review_data=data,
            duration=duration,
            state_before=spore
        )
        self._node_service.update_learning_unit(node.id, spore.slot, SporeUpdate(learning_data=type_data, last_review=now, due=datetime_to_ms(card.due)))
        return self._node_service.get_node(node.id)

    def review_fragment(
            self,
            col_id: str,
            fragment_id: str,
            duration: int,
            data: FragmentReviewData,
            tz_offset: int = 0,
    ) -> Node:
        node = self._node_service.get_node_from_learning_unit(fragment_id)
        fragment = node.get_fragment()
        rep_index = self.get_encounter_count(fragment_id) + 1
        depth = self._node_service.get_depth(node.id)
        next_interval = self._scheduling_engine.compute_fragment_next_interval(depth, rep_index)
        now = now_ms()
        self._repo.create(
            learning_unit_id=fragment_id,
            type=NodeType.FRAGMENT,
            type_review_data=data,
            duration=duration,
            state_before=fragment
        )
        due = start_of_local_day_ms(now + next_interval * MS_PER_DAY, tz_offset)
        self._node_service.update_learning_unit(node.id, fragment.slot, FragmentUpdate(due=due, last_review=now))
        return self._node_service.get_node(node.id)

    def get_encounter_count(self, learning_unit_id: str) -> int:
        return self._repo.get_encounter_count(learning_unit_id)

    def get_reviews_for_today(self, col_id: str, tz_offset_minutes: int = 0) -> list[Review]:
        today_start = start_of_local_today_ms(tz_offset_minutes)
        today_end = today_start + MS_PER_DAY
        return self._repo.get_by_period(today_start, today_end, col_id)

    def get_next_learning_unit_id(self, user_id: str, col_id: str, tz_offset: int = 0) -> str | None:
        nodes = self._node_service.get_scheduling_context(user_id, col_id)
        today_reviews = self.get_reviews_for_today(col_id, tz_offset)
        today_reviews_context = []

        for r in today_reviews:
            learning_unit = self._node_service.get_learning_unit(r.learning_unit_id, True)

            if not learning_unit:
                continue

            today_reviews_context.append(
                ReviewContext(
                    id=r.id,
                    learning_unit_type=NodeType(learning_unit.type),
                )
            )

        return self._scheduling_engine.get_next_learning_unit_id(user_id, nodes, today_reviews_context, tz_offset)

    def get_next_learning_unit(self, user_id: str, col_id: str, tz_offset: int = 0) -> LearningUnit | None:
        next_review_id = self.get_next_learning_unit_id(user_id, col_id, tz_offset)
        if not next_review_id:
            return None
        learning_unit = self._node_service.get_learning_unit(next_review_id)
        return learning_unit

    def undo_review(self, col_id: str, max_age_min: int | None = None) -> Review:
        last_review = self._repo.get_last_review_by_collection(col_id)

        if last_review is None:
            raise NoReviewToUndo()

        if max_age_min is not None:
            age = now_s() - (last_review.reviewed_at // 1000)
            max_age_s = max_age_min * 60
            if age > max_age_s:
                raise ReviewUndoNotAllowedError(age, max_age_s)

        self._repo.delete(last_review.id)
        
        return last_review
