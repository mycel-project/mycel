from src.domain.domain_exceptions import NoPendingNodeError, PendingReviewMismatchError, UnknownReviewTypeError
from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.services.node_service import NodeService
from src.services.review_service import ReviewService
from src.models.node import Node



class ReviewOrchestrator:
    def __init__(self, node_service: NodeService, review_service: ReviewService):
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

    def undo_review(self, col_id: int, max_age_s: int | None = 600) -> Node:
        last_review_node_id = self._review_service.undo_review(col_id, max_age_s)
        self._review_service.set_pending_node_id(last_review_node_id)
        return self._node_service.get_node(last_review_node_id)
