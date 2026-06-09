from typing import cast
import fsrs
import hashlib
import json

from src.domain.domain_exceptions import NotASpore
from src.models.spore import Spore
from src.services.node_service import NodeService
from .collection_service import CollectionService
from src.utils.time import ms_to_datetime, now_datetime


class FsrsService:
    def __init__(self, collection_service: CollectionService, node_service: NodeService):
        self._collection_service = collection_service
        self._node_service = node_service
        self._scheduler = None
        self._fsrs_conf_hash = None

    def _get_scheduler(self, user_id: str, col_id: str):
        fsrs_conf = self._collection_service.get_algo_conf(user_id, col_id) # only used for fsrs for now

        conf_dict = fsrs_conf.to_algo_dict()
        conf_hash = hashlib.md5(
            json.dumps(conf_dict, default=str).encode()
        ).hexdigest()

        if self._scheduler is None or self._fsrs_conf_hash != conf_hash:
            self._scheduler = fsrs.Scheduler(**conf_dict)
            self._fsrs_conf_hash = conf_hash

        return self._scheduler

    def review(self, user_id: str, col_id: str, learning_unit_id: str, rating: int, duration: int):
        scheduler = self._get_scheduler(user_id, col_id)
        now = now_datetime()
        card = self.convert_to_card(learning_unit_id)
        rating = fsrs.Rating(rating)
        return scheduler.review_card(card, rating, now, duration)

    def convert_to_card(self, learning_unit_id: str) -> fsrs.Card:
        learning_unit = self._node_service.get_learning_unit(learning_unit_id)
        if not isinstance(learning_unit, Spore):
            raise NotASpore(learning_unit.id)
        spore = cast(Spore, learning_unit)
        fsrs_data = spore.get_fsrs_data()
        return fsrs.Card(
            state=fsrs.State(fsrs_data.state),
            step=fsrs_data.step,
            stability=fsrs_data.stability,
            difficulty=fsrs_data.difficulty,
            due=ms_to_datetime(spore.due),
            last_review=ms_to_datetime(spore.last_review) if spore.last_review else None,
        )
