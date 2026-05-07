from unittest.mock import Mock

from src.domain.domain_exceptions import NoPendingNodeError, NotAFragment, NotASpore, PendingReviewMismatchError, UnknownReviewTypeError
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.services.review_orchestrator import ReviewOrchestrator

import pytest

from src.types.node_type import NodeType


# review_orchestrator

def test_review_mismatch():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = 10

    orchestrator = ReviewOrchestrator(node_service, review_service)

    with pytest.raises(PendingReviewMismatchError):
        orchestrator.review(col_id=1, node_id=20, data=Mock())

def test_review_unknown_type():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = 20

    orchestrator = ReviewOrchestrator(node_service, review_service)

    with pytest.raises(UnknownReviewTypeError):
        orchestrator.review(col_id=1, node_id=20, data=Mock())

def test_review_no_pending():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = None

    orchestrator = ReviewOrchestrator(node_service, review_service)

    with pytest.raises(NoPendingNodeError):
        orchestrator.review(1, 10, Mock())

def test_review_spore_success():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = 10
    review_service.review_spore = Mock()

    orchestrator = ReviewOrchestrator(node_service, review_service)

    data = SporeReviewData(duration=10, rating=1)

    orchestrator.review(1, 10, data)

    review_service.review_spore.assert_called_once()


# review_service

def test_review_fragment_not_fragment_node(review_service):
    node_service = review_service._node_service

    node_service.get_node.return_value = Mock(
        id=1,
        type=NodeType.SPORE,
        due=1000,
    )

    data = FragmentReviewData(duration=10)

    with pytest.raises(NotAFragment):
        review_service.review_fragment(1, 1, data)

def test_review_spore_not_spore_node(review_service):
    node_service = review_service._node_service

    node_service.get_node.return_value = Mock(
        id=1,
        type=NodeType.FRAGMENT,
        due=1000,
    )

    data = SporeReviewData(duration=10, rating=1)

    with pytest.raises(NotASpore):
        review_service.review_spore(1, 1, data)
