from src.domain.domain_exceptions import NoPendingNodeError, PendingReviewMismatchError, UnknownReviewTypeError
from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.services.node_service import NodeService
from src.services.review_service import ReviewService


class ReviewOrchestrator:
    def __init__(self, node_service: NodeService, review_service: ReviewService):
        self._node_service = node_service
        self._review_service = review_service

    def review(self, col_id: int, node_id: int, data: TypeReviewData):
        pending_review_id = self._review_service.get_pending_node_id()
        if pending_review_id is None:
            raise NoPendingNodeError(node_id)
        if pending_review_id != node_id:
            raise PendingReviewMismatchError(node_id, pending_review_id)
        if isinstance(data, SporeReviewData):
            self._review_service.review_spore(col_id, node_id, data)
        elif isinstance(data, FragmentReviewData):
            self._review_service.review_fragment(col_id, node_id, data)
        else:
            raise UnknownReviewTypeError(data.__class__.__name__)


