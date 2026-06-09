import time


from src.models.node import NodeFields, NodeType
from src.models.spore import Spore
from src.utils.time import local_date_to_utc_ms


def _due_ms(iso_utc: str) -> int:
    from datetime import datetime, timezone
    dt = datetime.strptime(iso_utc, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

class TestLearningUnitRepositoryBasic:
    def test_create_and_get(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.FRAGMENT)
        
        original_unit = node.learning_units[0]
        
        learning_unit_repo.delete(original_unit.id)
        assert learning_unit_repo.get(original_unit.id) is None
        
        created = learning_unit_repo.create(original_unit)
        assert created.id == original_unit.id
        
        fetched = learning_unit_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.node_id == node.id
        assert fetched.type == NodeType.FRAGMENT

    def test_get_by_node(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.FRAGMENT)
        
        units = learning_unit_repo.get_by_node(node.id)
        assert len(units) == 1
        assert units[0].node_id == node.id

    def test_get_by_nodes(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        node1 = create_node(col_id=col.id, user_id=user.id, type=NodeType.FRAGMENT)
        node2 = create_node(col_id=col.id, user_id=user.id, type=NodeType.FRAGMENT)
        
        units = learning_unit_repo.get_by_nodes([node1.id, node2.id])
        assert len(units) == 2
        
        node_ids = {u.node_id for u in units}
        assert node1.id in node_ids
        assert node2.id in node_ids
        
        assert learning_unit_repo.get_by_nodes([]) == []

    def test_update(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.FRAGMENT)
        
        unit = node.learning_units[0]
        unit.due = 99999
        
        learning_unit_repo.update(unit)
        
        updated = learning_unit_repo.get(unit.id)
        assert updated.due == 99999

    def test_delete(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.FRAGMENT)
        
        unit = node.learning_units[0]
        
        learning_unit_repo.delete(unit.id)
        assert learning_unit_repo.get(unit.id) is None

    def test_get_dues(self, learning_unit_repo, app, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)

        now = int(time.time() * 1000)
        node1 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        node2 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)

        lu1_id = node1.learning_units[0].id
        lu2_id = node2.learning_units[0].id

        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": now - 1000, "id": lu1_id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": now + 1000, "id": lu2_id})

        due_units = learning_unit_repo.get_dues(col.id, now_ms=now)

        assert len(due_units) == 1
        assert due_units[0].node_id == node1.id
    
class TestLearningUnitRepositoryPositions:
    def test_position_updates(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE, position="01")
        lu_id = node.learning_units[0].id
        
        assert learning_unit_repo.get_position(lu_id) == "01"
        
        learning_unit_repo.update_position(lu_id, "05")
        assert learning_unit_repo.get_position(lu_id) == "05"

    def test_position_queries(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE, position="A")
        create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE, position="B")
        create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE, position="C")

        assert learning_unit_repo.count_by_collection(col.id) == 3
        assert learning_unit_repo.count_before_position(col.id, "B") == 1
        
        assert learning_unit_repo.get_position_at_offset(col.id, 1) == "B"
        
        assert learning_unit_repo.get_tail_key(col.id) == "C"

    def test_get_all_positions(self, learning_unit_repo, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)

        n1 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE, position="X")
        n2 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE, position="Y")
        
        positions = learning_unit_repo.get_all_positions(col.id)
        assert len(positions) == 2
        assert positions[0] == (n1.get_unit_by_slot().id, "X")
        assert positions[1] == (n2.get_unit_by_slot().id, "Y")


class TestDueCountByTypeAndDay:
    def test_utc_basic_bucketing(self, learning_unit_repo, app, create_user, create_col, create_node):
        """Nodes due on the same UTC day are grouped together."""
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node_type = NodeType.SPORE
        due_a = _due_ms("2026-05-19 08:00:00")
        due_b = _due_ms("2026-05-19 22:00:00")

        node1 = create_node(col_id=col.id, user_id=user.id, type=node_type)
        node2 = create_node(col_id=col.id, user_id=user.id, type=node_type)

        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": due_a, "id": node1.learning_units[0].id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": due_b, "id": node2.learning_units[0].id})

        results = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)

        assert len(results) == 1
        day_ms, rtype, count = results[0]
        assert count == 2
        assert NodeType(rtype) == node_type

    def test_tz_offset_shifts_bucket(self, learning_unit_repo, app, create_user, create_col, create_node):
        """
        A node due at 2026-05-19 23:30 UTC is still on May 19 in UTC,
        but on May 20 for a UTC+1 user (offset=+60).
        """
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        due_ms = _due_ms("2026-05-19 23:30:00")
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": due_ms, "id": node.learning_units[0].id})

        results_utc = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)
        assert len(results_utc) == 1
        day_ms_utc = results_utc[0][0]
        assert day_ms_utc == _due_ms("2026-05-19 00:00:00")

        results_plus1 = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=60)
        assert len(results_plus1) == 1
        day_ms_plus1 = results_plus1[0][0]
        assert day_ms_plus1 == local_date_to_utc_ms("2026-05-20", tz_offset_minutes=60)

    def test_negative_tz_offset(self, learning_unit_repo, app, create_user, create_col, create_node):
        """
        A node due at 2026-05-20 00:30 UTC is on May 20 in UTC,
        but still on May 19 for a UTC-2 user (offset=-120).
        """
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        due_ms = _due_ms("2026-05-20 00:30:00")
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": due_ms, "id": node.learning_units[0].id})

        results_utc = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)
        assert results_utc[0][0] == _due_ms("2026-05-20 00:00:00")

        results_minus2 = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=-120)
        assert results_minus2[0][0] == local_date_to_utc_ms("2026-05-19", tz_offset_minutes=-120)

    def test_large_positive_offset(self, learning_unit_repo, app, create_user, create_col, create_node):
        """UTC+10 edge case: node at 2026-05-19 23:00 UTC = May 20 locally."""
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        due_ms = _due_ms("2026-05-19 23:00:00")
        node = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": due_ms, "id": node.learning_units[0].id})

        results = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=600)
        assert len(results) == 1
        assert results[0][0] == local_date_to_utc_ms("2026-05-20", tz_offset_minutes=600)

    def test_groups_by_type(self, learning_unit_repo, app, create_user, create_col, create_node):
        """Spores and fragments on the same day are returned as separate rows."""
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        day = "2026-05-19 10:00:00"
        node1 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        node2 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        node3 = create_node(col_id=col.id, user_id=user.id, type=NodeType.FRAGMENT)

        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": _due_ms(day), "id": node1.learning_units[0].id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": _due_ms(day), "id": node2.learning_units[0].id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": _due_ms(day), "id": node3.learning_units[0].id})

        results = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)

        by_type = {NodeType(r[1]): r[2] for r in results}
        assert by_type[NodeType.SPORE] == 2
        assert by_type[NodeType.FRAGMENT] == 1

    def test_start_end_filter(self, learning_unit_repo, app, create_user, create_col, create_node):
        """Nodes outside the [start_ms, to_ms) range are excluded."""
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node1 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        node2 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        node3 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)

        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": _due_ms("2026-05-01 12:00:00"), "id": node1.learning_units[0].id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": _due_ms("2026-05-15 12:00:00"), "id": node2.learning_units[0].id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": _due_ms("2026-05-31 12:00:00"), "id": node3.learning_units[0].id})

        start = _due_ms("2026-05-10 00:00:00")
        end = _due_ms("2026-05-20 00:00:00")

        results = learning_unit_repo.due_count_by_type_and_day(col.id, start, end, tz_offset_minutes=0)

        assert len(results) == 1
        assert results[0][2] == 1

    def test_nodes_split_across_days_by_timezone(self, learning_unit_repo, app, create_user, create_col, create_node):
        """
        Two nodes close in time but on different local days due to timezone
        must end up in two separate buckets.
        """
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        due_a = _due_ms("2026-05-19 23:30:00")
        due_b = _due_ms("2026-05-20 00:30:00")
        node1 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        node2 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)

        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": due_a, "id": node1.learning_units[0].id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": due_b, "id": node2.learning_units[0].id})

        results = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=60)

        assert len(results) == 1
        assert results[0][2] == 2

    def test_empty_default_collection(self, learning_unit_repo, create_user, create_col):
        """No nodes → empty result, no crash."""
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        results = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)
        assert results == []

    def test_midnight_boundary(self, learning_unit_repo, app, create_user, create_col, create_node):
        """23:59 and 00:00 UTC must be different days."""
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        before = _due_ms("2026-05-19 23:59:00")
        after  = _due_ms("2026-05-20 00:00:00")

        node1 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)
        node2 = create_node(col_id=col.id, user_id=user.id, type=NodeType.SPORE)

        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": before, "id": node1.learning_units[0].id})
        app.db.execute("UPDATE learning_units SET due = :due WHERE id = :id", {"due": after, "id": node2.learning_units[0].id})

        results = learning_unit_repo.due_count_by_type_and_day(col.id, 0, 2**63 - 1, tz_offset_minutes=0)

        assert len(results) == 2 
        assert results[0][2] == 1
        assert results[1][2] == 1
