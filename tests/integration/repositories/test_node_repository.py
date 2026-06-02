import time
import pytest
from src.repositories.node_repository import NodeRepository
from src.models.node_content import NodeContent
from src.types.node_type import NodeType
from src.utils.time import local_date_to_utc_ms


def _due_ms(iso_utc: str) -> int:
    from datetime import datetime, timezone
    dt = datetime.strptime(iso_utc, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

class TestNodeRepositoryBasic:
    def test_create_and_get(self, node_repo, default_collection):
        created = node_repo.create(
            collection_id=default_collection,
            content=NodeContent(),
            type=NodeType.SPORE,
            position="01"
        )
        assert created.id is not None
        
        fetched = node_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.position == "01"
        assert fetched.type == NodeType.SPORE

    def test_update(self, node_repo, default_collection):
        node = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "01")
        node.position = "02"
        node.due = 9999
        
        node_repo.update(node)
        
        updated = node_repo.get(node.id)
        assert updated.position == "02"
        assert updated.due == 9999

    def test_delete(self, node_repo, default_collection):
        node = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "01")
        node_repo.delete(node.id)
        assert node_repo.get(node.id) is None

class TestNodeRepositoryQueries:
    def test_get_by_collection(self, node_repo, default_collection):
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "01")
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "02")
        
        results = node_repo.get_by_collection(default_collection)
        assert len(results) == 2
        assert results[0].position == "01"

        limited = node_repo.get_by_collection(default_collection, limit=1)
        assert len(limited) == 1

    def test_get_by_type(self, node_repo, default_collection):
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "01")
        node_repo.create(default_collection, NodeContent(), NodeType.FRAGMENT, "02")
        
        spores = node_repo.get_by_type(default_collection, NodeType.SPORE.value)
        assert len(spores) == 1
        assert spores[0].type == NodeType.SPORE

    def test_get_due(self, node_repo, default_collection):
        now = int(time.time() * 1000)
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "01", due=now - 1000)
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "02", due=now + 10000)

        due_nodes = node_repo.get_due(default_collection, now_ms=now)
        assert len(due_nodes) == 1
        assert due_nodes[0].position == "01"

    def test_hierarchy(self, node_repo, default_collection):
        parent = node_repo.create(default_collection, NodeContent(), NodeType.FRAGMENT, "01")
        child1 = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "02", parent_id=parent.id)
        child2 = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "03", parent_id=child1.id)

        direct_children = node_repo.get_children(parent.id)
        assert len(direct_children) == 1
        assert direct_children[0].id == child1.id

        all_descendants = node_repo.get_children_recursive(parent.id)
        assert len(all_descendants) == 2

    def test_expired_deleted(self, node_repo, default_collection):
        node = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "01")
        node.deleted_at = 1000
        node_repo.update(node)

        expired = node_repo.get_expired_deleted(default_collection, cutoff_ms=2000)
        assert len(expired) == 1

        not_expired = node_repo.get_expired_deleted(default_collection, cutoff_ms=500)
        assert len(not_expired) == 0

class TestNodeRepositoryPositions:
    def test_position_updates(self, node_repo, default_collection):
        node = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "01")
        
        assert node_repo.get_position(node.id) == "01"
        
        node_repo.update_position(node.id, "05")
        assert node_repo.get_position(node.id) == "05"

    def test_position_queries(self, node_repo, default_collection):
        n1 = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "A")
        n2 = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "B")
        n3 = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "C")

        assert node_repo.count_by_collection(default_collection) == 3
        assert node_repo.count_before_position(default_collection, "B") == 1
        
        assert node_repo.get_position_at_offset(default_collection, 1) == "B"
        
        assert node_repo.get_tail_key(default_collection) == "C"

        assert node_repo.get_predecessor_position(default_collection, "B", n2.id) == "A"
        assert node_repo.get_successor_position(default_collection, "B", n2.id) == "C"

    def test_get_all_positions(self, node_repo, default_collection):
        n1 = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "X")
        n2 = node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "Y")
        
        positions = node_repo.get_all_positions(default_collection)
        assert len(positions) == 2
        assert positions[0] == (n1.id, "X")
        assert positions[1] == (n2.id, "Y")

class TestDueCountByTypeAndDay:
    def test_utc_basic_bucketing(self, node_repo, default_collection):
        """Nodes due on the same UTC day are grouped together."""
        node_type = NodeType.SPORE
        due_a = _due_ms("2026-05-19 08:00:00")
        due_b = _due_ms("2026-05-19 22:00:00")

        node_repo.create(default_collection, NodeContent(), node_type, "0", due=due_a)
        node_repo.create(default_collection, NodeContent(), node_type, "0", due=due_b)

        results = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=0)

        assert len(results) == 1
        day_ms, rtype, count = results[0]
        assert count == 2
        assert NodeType(rtype) == node_type

    def test_tz_offset_shifts_bucket(self, node_repo, default_collection):
        """
        A node due at 2026-05-19 23:30 UTC is still on May 19 in UTC,
        but on May 20 for a UTC+1 user (offset=+60).
        """
        due_ms = _due_ms("2026-05-19 23:30:00")
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=due_ms)

        results_utc = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=0)
        assert len(results_utc) == 1
        day_ms_utc = results_utc[0][0]
        assert day_ms_utc == _due_ms("2026-05-19 00:00:00")

        results_plus1 = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=60)
        assert len(results_plus1) == 1
        day_ms_plus1 = results_plus1[0][0]
        assert day_ms_plus1 == local_date_to_utc_ms("2026-05-20", tz_offset_minutes=60)

    def test_negative_tz_offset(self, node_repo, default_collection):
        """
        A node due at 2026-05-20 00:30 UTC is on May 20 in UTC,
        but still on May 19 for a UTC-2 user (offset=-120).
        """
        due_ms = _due_ms("2026-05-20 00:30:00")
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=due_ms)

        results_utc = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=0)
        assert results_utc[0][0] == _due_ms("2026-05-20 00:00:00")

        results_minus2 = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=-120)
        assert results_minus2[0][0] == local_date_to_utc_ms("2026-05-19", tz_offset_minutes=-120)

    def test_large_positive_offset(self, node_repo, default_collection):
        """UTC+10 edge case: node at 2026-05-19 23:00 UTC = May 20 locally."""
        due_ms = _due_ms("2026-05-19 23:00:00")
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=due_ms)

        results = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=600)
        assert len(results) == 1
        assert results[0][0] == local_date_to_utc_ms("2026-05-20", tz_offset_minutes=600)

    def test_groups_by_type(self, node_repo, default_collection):
        """Spores and fragments on the same day are returned as separate rows."""
        day = "2026-05-19 10:00:00"
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=_due_ms(day))
        time.sleep(0.002)
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=_due_ms(day))
        time.sleep(0.002)
        node_repo.create(default_collection, NodeContent(), NodeType.FRAGMENT, "0", due=_due_ms(day))

        results = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=0)

        by_type = {NodeType(r[1]): r[2] for r in results}
        assert by_type[NodeType.SPORE] == 2
        assert by_type[NodeType.FRAGMENT] == 1

    def test_start_end_filter(self, node_repo, default_collection):
        """Nodes outside the [start_ms, to_ms) range are excluded."""
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=_due_ms("2026-05-01 12:00:00"))
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=_due_ms("2026-05-15 12:00:00"))
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=_due_ms("2026-05-31 12:00:00"))

        start = _due_ms("2026-05-10 00:00:00")
        end = _due_ms("2026-05-20 00:00:00")

        results = node_repo.due_count_by_type_and_day(default_collection, start, end, tz_offset_minutes=0)

        assert len(results) == 1
        assert results[0][2] == 1

    def test_nodes_split_across_days_by_timezone(self, node_repo, default_collection):
        """
        Two nodes close in time but on different local days due to timezone
        must end up in two separate buckets.
        """
        due_a = _due_ms("2026-05-19 23:30:00")
        due_b = _due_ms("2026-05-20 00:30:00")
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=due_a)
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=due_b)

        results = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=60)

        assert len(results) == 1
        assert results[0][2] == 2

    def test_empty_default_collection(self, node_repo, default_collection):
        """No nodes → empty result, no crash."""
        results = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=0)
        assert results == []

    def test_midnight_boundary(self, node_repo, default_collection):
        """23:59 and 00:00 UTC must be different days."""
        before = _due_ms("2026-05-19 23:59:00")
        after  = _due_ms("2026-05-20 00:00:00")

        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=before)
        node_repo.create(default_collection, NodeContent(), NodeType.SPORE, "0", due=after)

        results = node_repo.due_count_by_type_and_day(default_collection, 0, 2**63 - 1, tz_offset_minutes=0)

        assert len(results) == 2 
        assert results[0][2] == 1
        assert results[1][2] == 1
