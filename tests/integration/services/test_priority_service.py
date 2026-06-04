import pytest


class TestGetPriority:
    def test_single_node_returns_zero(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        assert priority_service.get_priority(col.id, node.id) == 100

    def test_empty_collection(self, priority_service, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        with pytest.raises(ValueError):
            priority_service.get_priority(col.id, "nonexistent")


class TestGetPositionForPriority:
    def test_empty_collection(self, priority_service, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        position = priority_service.get_position_for_priority(col.id, 50)
        assert position is not None

    def test_priority_100_inserts_at_head(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        for i in range(5):
            position = priority_service.get_position_for_priority(col.id, 50)
            create_node(col_id=col.id, user_id=user.id, position = position)
        
        position_100 = priority_service.get_position_for_priority(col.id, 100)
        node_100 = create_node(col_id=col.id, user_id=user.id, position=position_100)
        
        assert priority_service.get_priority(col.id, node_100.id) == 100

    def test_priority_0_inserts_at_tail(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        for i in range(5):
            position = priority_service.get_position_for_priority(col.id, 50)
            create_node(col_id=col.id, user_id=user.id, position=position)
        
        position_0 = priority_service.get_position_for_priority(col.id, 0)
        node_0 = create_node(col_id=col.id, user_id=user.id, position=position_0)
        
        assert priority_service.get_priority(col.id, node_0.id) == 0

    def test_invalid_percentage(self, priority_service, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        with pytest.raises(ValueError):
            priority_service.get_position_for_priority(col.id, 101)
        with pytest.raises(ValueError):
            priority_service.get_position_for_priority(col.id, -1)


class TestReprioritiseNode:
    def test_moves_node_to_top(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        nodes = []
        for i in range(3):
            position = priority_service.get_position_for_priority(col.id, i * 33)
            nodes.append(create_node(col_id=col.id, user_id=user.id, position=position))
        
        lowest = min(nodes, key=lambda n: priority_service.get_priority(col.id, n.id))
        priority_service.reprioritise_node(col.id, lowest.id, 100)
        
        assert priority_service.get_priority(col.id, lowest.id) == 100

    def test_moves_node_to_bottom(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        nodes = []
        for i in range(3):
            position = priority_service.get_position_for_priority(col.id, 33 + i * 33)
            nodes.append(create_node(col_id=col.id, user_id=user.id, position=position))
        
        highest = max(nodes, key=lambda n: priority_service.get_priority(col.id, n.id))
        priority_service.reprioritise_node(col.id, highest.id, 0)
        
        assert priority_service.get_priority(col.id, highest.id) == 0


class TestPrioritiseRandomBetween:
    def test_inserts_within_range(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        for i in range(100):
            position = priority_service.get_position_for_priority(col.id, i)
            create_node(col_id=col.id, user_id=user.id, position = position)
        
        for _ in range(100):
            position = priority_service.prioritise_random_between_percentage(col.id, 30, 60)
            node = create_node(col_id=col.id, user_id=user.id, position=position)
            priority = priority_service.get_priority(col.id, node.id)
            assert 29 <= priority <= 61


class TestPrioritiseRandomNearNode:
    def test_child_is_more_prioritised_than_parent(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        for i in range(100):
            position = priority_service.get_position_for_priority(col.id, i)
            create_node(col_id=col.id, user_id=user.id, position=position)
             
        for _ in range(100):
            position = priority_service.get_position_for_priority(col.id, 50)
            parent = create_node(col_id=col.id, user_id=user.id, position = position)   
            position = priority_service.prioritise_random_near_node(col.id, parent.id, 10)
            child = create_node(col_id=col.id, user_id=user.id, position=position)
            assert priority_service.get_priority(col.id, child.id) >= priority_service.get_priority(col.id, parent.id)

    def test_sliding_near_100(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        for i in range(100):
            priority_service.get_position_for_priority(col.id, i)
            create_node(col_id=col.id, user_id=user.id)
        
        for _ in range(100):
            position = priority_service.get_position_for_priority(col.id, 95)
            high_node = create_node(col_id=col.id, user_id=user.id, position=position)
            position = priority_service.prioritise_random_near_node(col.id, high_node.id, 10)
            node = create_node(col_id=col.id, user_id=user.id, position=position)
            priority = priority_service.get_priority(col.id, node.id)
            assert 88 <= priority <= 100

    def test_sliding_near_0(self, priority_service, create_user, create_col, create_node):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        for i in range(100):
            position=priority_service.get_position_for_priority(col.id, i)
            create_node(col_id=col.id, user_id=user.id, position=position)
        
        priority_service.get_position_for_priority(col.id, 5)
        low_node = create_node(col_id=col.id, user_id=user.id)
        
        for _ in range(10):
            position = priority_service.prioritise_random_near_node(col.id, low_node.id, 10)
            node = create_node(col_id=col.id, user_id=user.id, position=position)
            priority = priority_service.get_priority(col.id, node.id)
            assert 0 <= priority <= 100
