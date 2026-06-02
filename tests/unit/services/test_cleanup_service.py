import pytest
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from src.models.user import User
from src.models.user_conf import UserConf
from src.services.cleanup_service import CleanupService
from src.models.node import Node


def make_node(id: int, deleted_at: int | None) -> Node:
    node = MagicMock(spec=Node)
    node.id = id
    node.deleted_at = deleted_at
    return node

def make_user(delete_max_age: int = 30) -> MagicMock:
    user = MagicMock()
    user.id = 1
    user.conf = UserConf(delete_max_age=delete_max_age)
    return user

def make_collection(id: int, name: str):
    col = MagicMock()
    col.id = id
    col.name = name
    return col


def cutoff_ms(days: int) -> int:
    return int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)

@pytest.fixture
def setup():
    user_service = MagicMock()
    node_service = MagicMock()
    collection_service = MagicMock()
    service = CleanupService(node_service, collection_service, user_service)
    return service, user_service, node_service, collection_service

class TestCleanDeletedNodes:
    @pytest.mark.asyncio
    async def test_expired_nodes_are_deleted(self, setup):
        cleanup_service, user_service, node_service, collection_service = setup
        user = make_user(delete_max_age=30)
        user_service.get_user.return_value = user
        collection = make_collection(1, "col1")
        collection_service.get_collections.return_value = [collection]

        expired_node = make_node(1, deleted_at=cutoff_ms(31)) 
        node_service.get_expired_deleted.return_value = [expired_node]

        await cleanup_service.clean_deleted_nodes()

        node_service.delete_node.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_no_expired_nodes(self, setup):
        cleanup_service, user_service, node_service, collection_service = setup
        user = make_user(delete_max_age=30)
        user_service.get_user.return_value = user
        collection = make_collection(1, "col1")
        collection_service.get_collections.return_value = [collection]
        node_service.get_expired_deleted.return_value = []

        await cleanup_service.clean_deleted_nodes()

        node_service.delete_node.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_collections(self, setup):
        cleanup_service, user_service, node_service, collection_service = setup
        user = make_user(delete_max_age=30)
        user_service.get_user.return_value = user
        collections = [make_collection(1, "col1"), make_collection(2, "col2")]
        collection_service.get_collections.return_value = collections
        node_service.get_expired_deleted.return_value = []

        await cleanup_service.clean_deleted_nodes()

        assert node_service.get_expired_deleted.call_count == 2

    @pytest.mark.asyncio
    async def test_multiple_expired_nodes(self, setup):
        cleanup_service, user_service, node_service, collection_service = setup
        user = make_user(delete_max_age=30)
        user_service.get_user.return_value = user
        collection = make_collection(1, "col1")
        collection_service.get_collections.return_value = [collection]

        expired_nodes = [make_node(i, deleted_at=cutoff_ms(31)) for i in range(5)]
        node_service.get_expired_deleted.return_value = expired_nodes

        await cleanup_service.clean_deleted_nodes()

        assert node_service.delete_node.call_count == 5

    @pytest.mark.asyncio
    async def test_no_collections(self, setup):
        cleanup_service, user_service, node_service, collection_service = setup
        user = make_user(delete_max_age=30)
        user_service.get_user.return_value = user
        collection_service.get_collections.return_value = []

        await cleanup_service.clean_deleted_nodes()

        node_service.delete_node.assert_not_called()
