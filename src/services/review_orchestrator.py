from src.domain.domain_exceptions import NoNodeFound, NoPendingNodeError, NodeDeleted, PendingReviewMismatchError, ReviewUndoNodeInaccessible, UnknownReviewTypeError
from src.models.review import Review
from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.schemas.node_update import NodeUpdate
from src.services.node_service import NodeService
from src.services.review_service import ReviewService
from src.models.node import Node
from src.services.user_service import UserService



class ReviewOrchestrator:
    def __init__(self, user_service: UserService, node_service: NodeService, review_service: ReviewService):
        self._user_service = user_service
        self._node_service = node_service
        self._review_service = review_service

    def review(self, col_id: int, node_id: int, duration: int, data: TypeReviewData):
        pending_review_id = self._review_service.get_pending_node_id()
        if pending_review_id is None:
            raise NoPendingNodeError(node_id)
        if pending_review_id != node_id:
            raise PendingReviewMismatchError(node_id, pending_review_id)
        if isinstance(data, SporeReviewData):
            self._review_service.review_spore(col_id, node_id, duration, data)
        elif isinstance(data, FragmentReviewData):
            self._review_service.review_fragment(col_id, node_id, duration, data)
        else:
            raise UnknownReviewTypeError(data.__class__.__name__)

    def _restore_node_from_snapshot(self, review: Review) -> None:
        self._node_service.update(
            review.node_id,
            NodeUpdate(
                last_review=review.node_state_before.last_review,
                due=review.node_state_before.due,
                type_data=review.node_state_before.type_data,
            )
        )

    def undo_review(self, col_id: int) -> Node:
        max_undo_age = self._user_service.get_undo_max_age_s(1)
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
        return self._node_service.get_node(node_from_undone_review.id)
