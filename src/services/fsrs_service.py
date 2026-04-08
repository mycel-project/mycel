from datetime import datetime, timedelta
import fsrs

from typing import Optional
from src.models.review import Review
from src.services.node_service import NodeService
from .collection_service import CollectionService
from src.utils.time import ms_to_datetime, now_datetime

class FsrsService:
    def __init__(self, collection_service: CollectionService, node_service: NodeService):
        self._collection_service = collection_service
        self._node_service = node_service
        self.init_scheduler()

    def init_scheduler(self):
        self._collection_service.get_fsrs_conf()
        self.scheduler = fsrs.Scheduler(
            parameters=(
                0.212, 1.2931, 2.3065, 8.2956, 6.4133,
                0.8334, 3.0194, 0.001, 1.8722, 0.1666,
                0.796, 1.4835, 0.0614, 0.2629, 1.6483,
                0.6014, 1.8729, 0.5425, 0.0912, 0.0658,
                0.1542
            ),
            desired_retention=0.9,
            learning_steps=(
                timedelta(seconds=60),
                timedelta(seconds=600),
            ),
            relearning_steps=(
                timedelta(seconds=600),
            ),
            maximum_interval=36500,
            enable_fuzzing=True,
        )

    def review_node(self, node_id: int, rating: int, duration: int):
        now = now_datetime()
        card = self.convert_card_to_node(node_id)
        rating = fsrs.Rating(rating)
        return self.scheduler.review_card(card, rating, now, duration)

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
