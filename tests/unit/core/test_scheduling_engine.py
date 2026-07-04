from src.core.scheduling_engine import SchedulingEngine
from src.models.node import NodeType


class TestSchedulingEngine:
    class TestGetDueLu:
        def test_dismiss_lu_ignored(self, scheduling_engine: SchedulingEngine, make_scheduling_context):
            learning_unit = make_scheduling_context(dismiss=False)
            due = scheduling_engine.get_due_lu(learning_units=[learning_unit])
            assert len(due) == 1
            learning_unit = make_scheduling_context(dismiss=True)
            due = scheduling_engine.get_due_lu(learning_units=[learning_unit])
            assert len(due) == 0
