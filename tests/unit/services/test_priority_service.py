from unittest.mock import MagicMock
from src.core.lexical_order import LexicalOrder
from src.services.priority_service import PriorityService


def test_position_to_priority_rounding():
    repo = MagicMock()
    priority_service = PriorityService(repo, LexicalOrder())

    repo.count_by_collection.return_value = 9
    repo.count_before_position.return_value = 7
    result = priority_service.position_to_priority("col", "pos")
    assert result == round(result, 0)

    repo.count_by_collection.return_value = 50
    repo.count_before_position.return_value = 43
    result = priority_service.position_to_priority("col", "pos")
    assert result == round(result, 1)

    repo.count_by_collection.return_value = 500
    repo.count_before_position.return_value = 432
    result = priority_service.position_to_priority("col", "pos")
    assert result == round(result, 2)

    repo.count_by_collection.return_value = 5000
    repo.count_before_position.return_value = 4321
    result = priority_service.position_to_priority("col", "pos")
    assert result == round(result, 3)

    repo.count_by_collection.return_value = 50000
    repo.count_before_position.return_value = 43210
    result = priority_service.position_to_priority("col", "pos")
    assert result == round(result, 4)

    repo.count_by_collection.return_value = 500000
    repo.count_before_position.return_value = 432100
    result = priority_service.position_to_priority("col", "pos")
    assert result == round(result, 5)
