from datetime import datetime, timezone

from src.types.node_type import NodeType
from src.types.count_by_type_and_day import CountByTypeAndDay

class TestNodeService:
    class TestGetDueCountByTypeAndDay:
        def test_both_types_same_day(self, node_service):
            ts = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)

            node_service._repo.due_count_by_type_and_day.return_value = [
                (ts, NodeType.SPORE.value, 3),
                (ts, NodeType.FRAGMENT.value, 7),
            ]

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == [
                CountByTypeAndDay(local_day_midnight_ms=ts, type=NodeType.SPORE, count=3),
                CountByTypeAndDay(local_day_midnight_ms=ts, type=NodeType.FRAGMENT, count=7),
            ]

        def test_only_spores(self, node_service):
            ts = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)

            node_service._repo.due_count_by_type_and_day.return_value = [
                (ts, NodeType.SPORE.value, 5),
            ]

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == [
                CountByTypeAndDay(local_day_midnight_ms=ts, type=NodeType.SPORE, count=5),
            ]

        def test_only_fragments(self, node_service):
            ts = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)

            node_service._repo.due_count_by_type_and_day.return_value = [
                (ts, NodeType.FRAGMENT.value, 9),
            ]

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == [
                CountByTypeAndDay(local_day_midnight_ms=ts, type=NodeType.FRAGMENT, count=9),
            ]

        def test_multiple_days(self, node_service):
            ts1 = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)
            ts2 = int(datetime(2026, 5, 19, tzinfo=timezone.utc).timestamp() * 1000)

            node_service._repo.due_count_by_type_and_day.return_value = [
                (ts1, NodeType.SPORE.value, 2),
                (ts2, NodeType.FRAGMENT.value, 4),
                (ts2, NodeType.SPORE.value, 1),
            ]

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == [
                CountByTypeAndDay(local_day_midnight_ms=ts1, type=NodeType.SPORE, count=2),
                CountByTypeAndDay(local_day_midnight_ms=ts2, type=NodeType.FRAGMENT, count=4),
                CountByTypeAndDay(local_day_midnight_ms=ts2, type=NodeType.SPORE, count=1),
            ]

        def test_empty(self, node_service):
            node_service._repo.due_count_by_type_and_day.return_value = []

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == []
