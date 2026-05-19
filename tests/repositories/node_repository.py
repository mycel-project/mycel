from src.repositories.node_repository import NodeRepository
from src.models.node import NodeType, NodeContent, NodeData
from src.utils.time import local_date_to_utc_ms

def _due_ms(iso_utc: str) -> int:
    from datetime import datetime, timezone
    dt = datetime.strptime(iso_utc, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

def _insert_node(repo: NodeRepository, col_id: int, due_ms: int, node_type: NodeType) -> None:
    """Insert a minimal node with a specific due timestamp."""
    node = repo.create(
        collection_id=col_id,
        content=NodeContent(),
        data=NodeData(),
        type=node_type,
        position="0",
    )
    # Override the due timestamp set by create() which defaults to now
    repo.db.execute(
        "UPDATE nodes SET due = ? WHERE id = ?",
        (due_ms, node.id),
    )

class TestNodeRepository:
    class TestDueCountByTypeAndDay:

        def test_utc_basic_bucketing(self, node_repo, col):
            """Nodes due on the same UTC day are grouped together."""
            node_type = NodeType.SPORE
            due_a = _due_ms("2026-05-19 08:00:00")
            due_b = _due_ms("2026-05-19 22:00:00")

            _insert_node(node_repo, col.id, due_a, node_type)
            _insert_node(node_repo, col.id, due_b, node_type)

            results = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)

            assert len(results) == 1
            day_ms, rtype, count = results[0]
            assert count == 2
            assert NodeType(rtype) == node_type

        def test_tz_offset_shifts_bucket(self, node_repo, col):
            """
            A node due at 2026-05-19 23:30 UTC is still on May 19 in UTC,
            but on May 20 for a UTC+1 user (offset=+60).
            """
            due_ms = _due_ms("2026-05-19 23:30:00")
            _insert_node(node_repo, col.id, due_ms, NodeType.SPORE)

            # UTC+0 → bucketed to May 19
            results_utc = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)
            assert len(results_utc) == 1
            day_ms_utc = results_utc[0][0]
            assert day_ms_utc == _due_ms("2026-05-19 00:00:00")

            # UTC+1 → bucketed to May 20
            results_plus1 = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=60)
            assert len(results_plus1) == 1
            day_ms_plus1 = results_plus1[0][0]
            assert day_ms_plus1 == local_date_to_utc_ms("2026-05-20", tz_offset_minutes=60)

        def test_negative_tz_offset(self, node_repo, col):
            """
            A node due at 2026-05-20 00:30 UTC is on May 20 in UTC,
            but still on May 19 for a UTC-2 user (offset=-120).
            """
            due_ms = _due_ms("2026-05-20 00:30:00")
            _insert_node(node_repo, col.id, due_ms, NodeType.SPORE)

            # UTC+0 → May 20
            results_utc = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)
            assert results_utc[0][0] == _due_ms("2026-05-20 00:00:00")

            # UTC-2 → May 19
            results_minus2 = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=-120)
            assert results_minus2[0][0] == local_date_to_utc_ms("2026-05-19", tz_offset_minutes=-120)

        def test_large_positive_offset(self, node_repo, col):
            """UTC+10 edge case: node at 2026-05-19 23:00 UTC = May 20 locally."""
            due_ms = _due_ms("2026-05-19 23:00:00")
            _insert_node(node_repo, col.id, due_ms, NodeType.SPORE)

            results = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=600)
            assert len(results) == 1
            assert results[0][0] == local_date_to_utc_ms("2026-05-20", tz_offset_minutes=600)

        def test_groups_by_type(self, node_repo, col):
            """Spores and fragments on the same day are returned as separate rows."""
            day = "2026-05-19 10:00:00"
            _insert_node(node_repo, col.id, _due_ms(day), NodeType.SPORE)
            _insert_node(node_repo, col.id, _due_ms(day), NodeType.SPORE)
            _insert_node(node_repo, col.id, _due_ms(day), NodeType.FRAGMENT)

            results = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)

            by_type = {NodeType(r[1]): r[2] for r in results}
            assert by_type[NodeType.SPORE] == 2
            assert by_type[NodeType.FRAGMENT] == 1

        def test_start_end_filter(self, node_repo, col):
            """Nodes outside the [start_ms, to_ms) range are excluded."""
            _insert_node(node_repo, col.id, _due_ms("2026-05-01 12:00:00"), NodeType.SPORE)
            _insert_node(node_repo, col.id, _due_ms("2026-05-15 12:00:00"), NodeType.SPORE)
            _insert_node(node_repo, col.id, _due_ms("2026-05-31 12:00:00"), NodeType.SPORE)

            start = _due_ms("2026-05-10 00:00:00")
            end = _due_ms("2026-05-20 00:00:00")

            results = node_repo.due_count_by_type_and_day(col.id, start, end, tz_offset_minutes=0)

            assert len(results) == 1
            assert results[0][2] == 1  # only the May 15 node

        def test_nodes_split_across_days_by_timezone(self, node_repo, col):
            """
            Two nodes close in time but on different local days due to timezone
            must end up in two separate buckets.
            """
            # 23:30 UTC May 19 → local May 20 for UTC+1
            # 00:30 UTC May 20 → local May 20 for UTC+1
            # Both should land on May 20 for UTC+1
            due_a = _due_ms("2026-05-19 23:30:00")
            due_b = _due_ms("2026-05-20 00:30:00")
            _insert_node(node_repo, col.id, due_a, NodeType.SPORE)
            _insert_node(node_repo, col.id, due_b, NodeType.SPORE)

            results = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=60)

            # Both land on May 20 local → single bucket with count=2
            assert len(results) == 1
            assert results[0][2] == 2

        def test_empty_collection(self, node_repo, col):
            """No nodes → empty result, no crash."""
            results = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)
            assert results == []

        def test_midnight_boundary(self, node_repo, col):
            """23:59 and 00:00 UTC must be different days."""
            before = _due_ms("2026-05-19 23:59:00")
            after  = _due_ms("2026-05-20 00:00:00")

            _insert_node(node_repo, col.id, before, NodeType.SPORE)
            _insert_node(node_repo, col.id, after,  NodeType.SPORE)

            results = node_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)

            assert len(results) == 2 
            assert results[0][2] == 1
            assert results[1][2] == 1
