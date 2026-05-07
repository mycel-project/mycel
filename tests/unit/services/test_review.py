from unittest.mock import Mock

from src.domain.domain_exceptions import NoPendingNodeError, NoReviewToUndo, NotAFragment, NotASpore, PendingReviewMismatchError, UndoNotAllowedError, UnknownReviewTypeError
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.services.review_orchestrator import ReviewOrchestrator

import pytest

from src.types.node_type import NodeType
from src.utils.time import now_ms


# review_orchestrator

def test_review_mismatch():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = 10

    orchestrator = ReviewOrchestrator(node_service, review_service)

    with pytest.raises(PendingReviewMismatchError):
        orchestrator.review(col_id=1, node_id=20, duration=10, data=Mock())

def test_review_unknown_type():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = 20

    orchestrator = ReviewOrchestrator(node_service, review_service)

    with pytest.raises(UnknownReviewTypeError):
        orchestrator.review(col_id=1, node_id=20, duration=10, data=Mock())

def test_review_no_pending():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = None

    orchestrator = ReviewOrchestrator(node_service, review_service)

    with pytest.raises(NoPendingNodeError):
        orchestrator.review(1, 10, duration=10, data=Mock())

def test_review_spore_success():
    review_service = Mock()
    node_service = Mock()

    review_service.get_pending_node_id.return_value = 10
    review_service.review_spore = Mock()

    orchestrator = ReviewOrchestrator(node_service, review_service)

    data = SporeReviewData(rating=1)

    orchestrator.review(1, 10, duration=10, data=data)

    review_service.review_spore.assert_called_once()


# review_service

def test_review_fragment_not_fragment_node(review_service):
    node_service = review_service._node_service

    node_service.get_node.return_value = Mock(
        id=1,
        type=NodeType.SPORE,
        due=1000,
    )

    data = FragmentReviewData()

    with pytest.raises(NotAFragment):
        review_service.review_fragment(1, 1, 10, data)

def test_review_spore_not_spore_node(review_service):
    node_service = review_service._node_service

    node_service.get_node.return_value = Mock(
        id=1,
        type=NodeType.FRAGMENT,
        due=1000,
    )

    data = SporeReviewData(rating=1)

    with pytest.raises(NotASpore):
        review_service.review_spore(1, 1, 10, data)

## Undo
        
def test_undo_review_success(review_service):
    repo = review_service._repo

    repo.get_last_review_by_collection.return_value = Mock(
        id=1,
        time=now_ms() - 10000 
    )

    review_service.undo_review(col_id=1, max_age_s=500)

    repo.delete.assert_called_once_with(1)

def test_undo_review_no_review(review_service):
    repo = review_service._repo

    repo.get_last_review_by_collection.return_value = None

    with pytest.raises(NoReviewToUndo):
        review_service.undo_review(col_id=1, max_age_s=500)

    repo.delete.assert_not_called()

def test_undo_review_too_old(review_service):
    repo = review_service._repo

    repo.get_last_review_by_collection.return_value = Mock(
        id=1,
        time=now_ms() - 1000000
    )

    with pytest.raises(UndoNotAllowedError):
        review_service.undo_review(col_id=1, max_age_s=100)

    repo.delete.assert_not_called()
