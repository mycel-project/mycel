from datetime import date
from datetime import timezone, timedelta, datetime

from src.domain.domain_exceptions import NoNodeFound, NoPendingReviewError, NodeDeleted, PendingReviewMismatchError, ReviewUndoLearningUnitInaccessible
from src.models.day_review_overview import DayReviewOverview
from src.models.dto.review_target import ReviewTarget
from src.models.node import NodeType
from src.models.review import Review
from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.schemas.node_detail_view import NodeDetailView
from src.services.collection_service import CollectionService
from src.services.node_service import NodeService
from src.services.node_view_builder import NodeViewBuilder
from src.services.review_service import ReviewService
from src.services.user_service import UserService


class ReviewOrchestrator:
    def __init__(self, user_service: UserService, node_service: NodeService, review_service: ReviewService, node_view_builder: NodeViewBuilder, collection_service: CollectionService):
        self._user_service = user_service
        self._node_service = node_service
        self._review_service = review_service
        self._node_view_builder = node_view_builder
        self._collection_service = collection_service

    def _ensure_col(self, user_id: str, col_id: str) -> None:
        self._collection_service.get_collection(user_id, col_id)

    def review_to_detail_view(self, user_id: str, col_id: str, node_id: str, slot: int, duration: int, data: TypeReviewData, tz_offset_min: int = 0) -> NodeDetailView:
        node = self._node_service.get_node_for_user(user_id, col_id, node_id)
        learning_unit = node.get_unit_by_slot(slot)
        pending_review_id = self._user_service.get_pending_review(user_id)
        if pending_review_id is None:
            raise NoPendingReviewError(learning_unit.id)
        if pending_review_id != learning_unit.id:
            raise PendingReviewMismatchError(learning_unit.id, pending_review_id)
        if isinstance(data, SporeReviewData):
            node = self._review_service.review_spore(user_id, col_id, learning_unit.id, duration, data)
        elif isinstance(data, FragmentReviewData):
            node = self._review_service.review_fragment(col_id, learning_unit.id, duration, data, tz_offset_min)
        self._user_service.clear_pending_review(user_id)
        return self._node_view_builder.to_detail_view(node)

    def _restore_from_snapshot(self, review: Review) -> None:
        self._node_service.update_learning_unit(review.state_before)

    def get_next_review(self, user_id: str, col_id: str, tz_offset: int = 0) -> ReviewTarget | None:
        self._ensure_col(user_id, col_id)
        learning_unit = self._review_service.get_next_learning_unit(user_id, col_id, tz_offset)
        if learning_unit is None:
            return None
        self._user_service.set_pending_review(user_id, learning_unit.id)
        node = self._node_service.get_node_from_learning_unit(learning_unit.id)
        return ReviewTarget(
            node=self._node_view_builder.to_detail_view(node),
            slot=getattr(learning_unit, 'slot', 0)
        )

    def undo_review(self, user_id: str, col_id: str) -> ReviewTarget:
        self._ensure_col(user_id, col_id)
        max_undo_age = self._user_service.get_undo_max_age_min(user_id)
        last_review = self._review_service.undo_review(col_id, max_undo_age)
        try:
            node_from_undone_review = self._node_service.get_node_from_learning_unit(last_review.learning_unit_id)
        except NodeDeleted as e:
            self._restore_from_snapshot(last_review)
            raise ReviewUndoLearningUnitInaccessible(last_review.learning_unit_id, last_review.id) from e
        except NoNodeFound as e:
            raise ReviewUndoLearningUnitInaccessible(last_review.learning_unit_id, last_review.id) from e
        self._restore_from_snapshot(last_review)
        self._user_service.set_pending_review(user_id, node_from_undone_review.id)
        node = self._node_service.get_node(node_from_undone_review.id)
        learning_unit = self._node_service.get_learning_unit(last_review.learning_unit_id)
        return ReviewTarget(
            node=self._node_view_builder.to_detail_view(node),
            slot=getattr(learning_unit, 'slot', 0)
        )

    def get_calendar(
        self,
        user_id: str,
        col_id: str,
        due: bool = True,
        done: bool = False,
        start=None,
        end=None,
        tz_offset_minutes: int = 0,
    ) -> list[DayReviewOverview]:
        self._ensure_col(user_id, col_id)
        # Use review service to get done for that period
        # Must determine which format to use to handle due/done. Timestamps ? iso ? What is cleaner for frontend ? maybe iso as we send back iso and it's only day specific ?

        calendar: dict[date, DayReviewOverview] = {}

        if due:
            for row in self._node_service.get_due_count_by_type_and_day(col_id, start, end, tz_offset_minutes):

                # directly return in local tz
                tz = timezone(timedelta(minutes=tz_offset_minutes))
                day = datetime.fromtimestamp(row.local_day_midnight_ms / 1000, tz=tz).date() 

                if day not in calendar:
                    calendar[day] = DayReviewOverview(date=day.isoformat())

                entry = calendar[day]

                if row.type == NodeType.SPORE:
                    entry.due_spores = row.count

                elif row.type == NodeType.FRAGMENT:
                    entry.due_fragments = row.count

        return sorted(
            calendar.values(),
            key=lambda d: d.date
        )
