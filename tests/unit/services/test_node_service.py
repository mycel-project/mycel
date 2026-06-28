from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.models.node import NodeType
from src.models.node_data import NodeData
from src.schemas.learning_unit_update import FragmentUpdate, LearningUnitUpdate
from src.schemas.node_update import NodeUpdate
from src.types.count_by_type_and_day import CountByTypeAndDay

class TestNodeService:
    class TestGetDueCountByTypeAndDay:
        def test_both_types_same_day(self, node_service):
            ts = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)

            node_service._lu_repo.due_count_by_type_and_day.return_value = [
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

            node_service._lu_repo.due_count_by_type_and_day.return_value = [
                (ts, NodeType.SPORE.value, 5),
            ]

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == [
                CountByTypeAndDay(local_day_midnight_ms=ts, type=NodeType.SPORE, count=5),
            ]

        def test_only_fragments(self, node_service):
            ts = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)

            node_service._lu_repo.due_count_by_type_and_day.return_value = [
                (ts, NodeType.FRAGMENT.value, 9),
            ]

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == [
                CountByTypeAndDay(local_day_midnight_ms=ts, type=NodeType.FRAGMENT, count=9),
            ]

        def test_multiple_days(self, node_service):
            ts1 = int(datetime(2026, 5, 18, tzinfo=timezone.utc).timestamp() * 1000)
            ts2 = int(datetime(2026, 5, 19, tzinfo=timezone.utc).timestamp() * 1000)

            node_service._lu_repo.due_count_by_type_and_day.return_value = [
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
            node_service._lu_repo.due_count_by_type_and_day.return_value = []

            result = node_service.get_due_count_by_type_and_day(1)

            assert result == []

    class TestNodeUpdate:
        def test_title_update(self, node_service, default_fragment):
            node_service.get_node = MagicMock(return_value=default_fragment)
            assert default_fragment.data.title == "title"
            assert default_fragment.collection_id == "test"
            assert default_fragment.data.source.url == "https://mycel-project.com"
            node_service._node_repo = MagicMock()
            node_service._hydrate_nodes = MagicMock()
            updates = NodeUpdate(data=NodeData(title="New Title"))
            result = node_service.update(default_fragment.id, updates)
            assert result.data.title == "New Title"
            assert result.collection_id == "test"
            assert result.data.source.url == "https://mycel-project.com"


    class TestUpdateLearningUnit:
        def test_dismiss_update(self, node_service, default_fragment):
            node_service.get_node = MagicMock(return_value=default_fragment)
            node_service._lu_repo = MagicMock()

            result = node_service.update_learning_unit(
                default_fragment.id,
                1,
                FragmentUpdate(dismiss=True)
            )

            fragment = result.get_fragment()
            assert fragment.dismiss == True
            
            result = node_service.update_learning_unit(
                default_fragment.id,
                1,
                FragmentUpdate(dismiss=False)
            )

            fragment = result.get_fragment()
            assert fragment.dismiss == False
            assert fragment.slot == 1
            assert fragment.ref == default_fragment.get_fragment().ref
