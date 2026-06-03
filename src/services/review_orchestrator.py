from datetime import date
from datetime import timezone, timedelta, datetime

from src.domain.domain_exceptions import NoNodeFound, NoPendingNodeError, NodeDeleted, PendingReviewMismatchError, ReviewUndoNodeInaccessible, UnknownReviewTypeError
from src.models.day_review_overview import DayReviewOverview
from src.models.review import Review
from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.schemas.node_detail_view import NodeDetailView
from src.schemas.node_update import NodeUpdate
from src.schemas.node_view import NodeView
from src.services.node_service import NodeService
from src.services.node_view_builder import NodeViewBuilder
from src.services.review_service import ReviewService
from src.services.user_service import UserService
from src.types.node_type import NodeType


class ReviewOrchestrator:
    def __init__(self, user_service: UserService, node_service: NodeService, review_service: ReviewService, node_view_builder: NodeViewBuilder):
        self._user_service = user_service
        self._node_service = node_service
        self._review_service = review_service
        self._node_view_builder = node_view_builder

    def review_to_detail_view(self, col_id: int, node_id: int, duration: int, data: TypeReviewData, tz_offset_min: int = 0) -> NodeDetailView:
        pending_review_id = self._review_service.get_pending_node_id()
        if pending_review_id is None:
            raise NoPendingNodeError(node_id)
        if pending_review_id != node_id:
            raise PendingReviewMismatchError(node_id, pending_review_id)
        if isinstance(data, SporeReviewData):
            node = self._review_service.review_spore(col_id, node_id, duration, data) # FSRS does not need tz
        elif isinstance(data, FragmentReviewData):
            node = self._review_service.review_fragment(col_id, node_id, duration, data, tz_offset_min)
        else:
            raise UnknownReviewTypeError(data.__class__.__name__)
        return self._node_view_builder.to_detail_view(node)

    def _restore_node_from_snapshot(self, review: Review) -> None:
        self._node_service.update(
            review.node_id,
            NodeUpdate(
                last_review=review.node_state_before.last_review,
                due=review.node_state_before.due,
                type_data=review.node_state_before.type_data,
            ),
            True
        )

    def get_next_review(self, col_id: int, tz_offset: int = 0) -> NodeDetailView | None:
        node = self._review_service.get_next_review(col_id, tz_offset)
        if node:
            return self._node_view_builder.to_detail_view(node)
        else:
            return None

    def undo_review(self, col_id: int) -> NodeDetailView:
        max_undo_age = self._user_service.get_undo_max_age_min(1)
        last_review = self._review_service.undo_review(col_id, max_undo_age)
        try:
            node_from_undone_review = self._node_service.get_node(last_review.node_id)
        except NodeDeleted as e:
            self._restore_node_from_snapshot(last_review)
            raise ReviewUndoNodeInaccessible(last_review.node_id, last_review.id) from e
        except NoNodeFound as e:
            raise ReviewUndoNodeInaccessible(last_review.node_id, last_review.id) from e
        self._restore_node_from_snapshot(last_review)
        self._review_service.set_pending_node_id(node_from_undone_review.id)
        node = self._node_service.get_node(node_from_undone_review.id)
        return self._node_view_builder.to_detail_view(node)

    def get_calendar(
        self,
        col_id,
        due: bool = True,
        done: bool = False,
        start=None,
        end=None,
        tz_offset_minutes: int = 0,
    ) -> list[DayReviewOverview]:
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
