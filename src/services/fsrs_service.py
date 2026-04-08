import fsrs
import hashlib
import json

from src.services.node_service import NodeService
from .collection_service import CollectionService
from src.utils.time import ms_to_datetime, now_datetime


class FsrsService:
    def __init__(self, collection_service: CollectionService, node_service: NodeService):
        self._collection_service = collection_service
        self._node_service = node_service
        self._scheduler = None
        self._fsrs_conf_hash = None

    def _get_scheduler(self, col_id: int):
        fsrs_conf = self._collection_service.get_fsrs_conf(col_id)

        conf_dict = fsrs_conf.to_fsrs_dict()
        conf_hash = hashlib.md5(
            json.dumps(conf_dict, default=str).encode()
        ).hexdigest()

        if self._scheduler is None or self._fsrs_conf_hash != conf_hash:
            self._scheduler = fsrs.Scheduler(**conf_dict)
            self._fsrs_conf_hash = conf_hash

        return self._scheduler

    def review_node(self, col_id: int, node_id: int, rating: int, duration: int):
        scheduler = self._get_scheduler(col_id)
        now = now_datetime()
        card = self.convert_card_to_node(node_id)
        rating = fsrs.Rating(rating)
        return scheduler.review_card(card, rating, now, duration)

    def convert_card_to_node(self, node_id: int) -> fsrs.Card:
        node = self._node_service.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        return fsrs.Card(
            card_id=node.id,
            state=fsrs.State(node.state),
            step=node.step,
            stability=node.stability,
            difficulty=node.difficulty,
            due=ms_to_datetime(node.due),
            last_review=ms_to_datetime(node.last_review) if node.last_review else None,
        )
