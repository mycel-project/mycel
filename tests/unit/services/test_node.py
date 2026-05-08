from unittest.mock import Mock, patch, call
from src.services.node_service import NodeService
from src.schemas.node_update import NodeUpdate
import pytest


def make_service():
    db = Mock()
    ressource_service = Mock()
    priority_service = Mock()
    return NodeService(db, ressource_service, priority_service)

def make_node(id: int):
    node = Mock()
    node.id = id
    return node

def test_soft_delete_node_calls_update_with_deleted_at():
    service = make_service()
    service.update = Mock(return_value=make_node(1))

    with patch('src.services.node_service.now_ms', return_value=12345):
        service.soft_delete_node(1)

    service.update.assert_called_once_with(1, NodeUpdate(deleted_at=12345))


def test_soft_delete_subtree_soft_deletes_all_nodes_and_returns_ids():
    service = make_service()
    nodes = [make_node(i) for i in [1, 2, 3]]
    service.get_subtree = Mock(return_value=nodes)
    service.soft_delete_node = Mock(return_value=make_node(0))

    ids = service.soft_delete_subtree(1)

    service.soft_delete_node.assert_has_calls([call(1), call(2), call(3)])
    assert ids == [1, 2, 3]
