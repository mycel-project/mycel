from datetime import datetime, timedelta, timezone
import logging

from src.services.collection_service import CollectionService
from src.services.node_service import NodeService
from src.services.user_service import UserService

logger = logging.getLogger(__name__)


class CleanupService():
    def __init__(
        self,
        node_service: NodeService,
        collection_service: CollectionService,
        user_service: UserService
    ):
        self._node_service = node_service
        self._collection_service = collection_service
        self._user_service = user_service

    async def clean_deleted_nodes(self):
        user = self._user_service.get_user(1)
        cutoff_ms = int((datetime.now(timezone.utc) - timedelta(days=user.conf.delete_max_age)).timestamp() * 1000)

        collections = self._collection_service.get_collections(user.id)
        for collection in collections:
            expired = self._node_service.get_expired_deleted(collection.id, cutoff_ms)
            for node in expired:
                self._node_service.delete_node(node.id)
            logger.info(f"Cleaned {len(expired)} expired nodes from collection {collection.name}")
