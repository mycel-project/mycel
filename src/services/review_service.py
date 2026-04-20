from typing import Optional, cast
from src.core.node_scheduling_context import NodeSchedulingContext
from src.core.review_context import ReviewContext
from src.db import Db
from src.models.review import Review
from src.models.type_data.fragment_data import FragmentData
from src.models.type_data.spore_data import SporeData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.repositories.review_repository import ReviewRepository
from src.core.scheduling_engine import SchedulingEngine
from src.schemas.fragment_review import FragmentReview
from src.schemas.spore_review import SporeReview
from src.schemas.node_review import NodeReview
from src.schemas.node_update import NodeUpdate
from src.services.fsrs_service import FsrsService
from src.types.node_type import NodeType
from src.utils.cloze import cloze_to_ellipsis, cloze_to_plain, cloze_with_wrapper
from .node_service import NodeService
from src.utils.time import add_days_ms, datetime_to_ms, end_of_day_ms, now_ms, start_of_day_ms
from src.models.node import Node

class ReviewService:
    # No caching at the moment
    def __init__(self, db: Db, scheduling_engine: SchedulingEngine, fsrs_service: FsrsService, node_service: NodeService):
        self._repo = ReviewRepository(db)
        self._fsrs_service = fsrs_service
        self._node_service = node_service
        self._scheduling_engine = scheduling_engine

    def review_spore(
            self,
            col_id: int,
            node_id: int,
            rating: int,
            duration: int,
    ) -> None:
        card, review_log = self._fsrs_service.review_node(col_id, node_id, rating, duration)
        node = self._node_service.get_node(node_id)
        if not node:
            raise ValueError(f"No node with id {node_id} found.")
        now = int(review_log.review_datetime.timestamp() * 1000)
        type_data = SporeData(
            stability=card.stability,
            difficulty=card.difficulty,
            state=int(card.state.value),
            step=card.step,
        )
        self._repo.create(
            node_id=node_id,
            type=node.type,
            type_review_data=SporeReviewData(
                rating=rating
            ),
            duration=duration,
            now=now
        )
        self._node_service.update(
            node_id,
            NodeUpdate(
                type_data=type_data,
                due=datetime_to_ms(card.due),
                last_review=now
            )
        )

    def review_fragment(
            self,
            col_id: int,
            node_id: int,
            duration: int,
    ) -> None:
        node = self._node_service.get_node(node_id)
        if not node:
            raise ValueError(f"No node found with id {node_id}")            
        if not node.type == NodeType.FRAGMENT:
            raise ValueError("Node must be from fragment type.")
        encounter_count = self.get_encounter_count(node_id)
        context = NodeSchedulingContext(
            id=node.id,
            type=node.type,
            encounter_count=encounter_count,
            due=node.due,
        )
        next_interval = self._scheduling_engine.next_linear_interval(context)
        now = now_ms()

        self._repo.create(
            node_id=node_id,
            type=node.type,
            type_review_data=FragmentReviewData(),
            duration=duration,
            now=now
        )
        self._node_service.update(
            node.id,
            NodeUpdate(
                type_data=FragmentData(),
                due=add_days_ms(now, next_interval),
                last_review=now
            )
        )

    def get_encounter_count(self, node_id: int) -> int:
        return self._repo.get_encounter_count(node_id)
    
    def get_reviews_for_today(self) -> list[Review]:
        now = now_ms()
        today_start = start_of_day_ms(now)
        today_end = end_of_day_ms(now)
        return self._repo.get_by_period(today_start, today_end)

    def get_next_review_id(self, col_id: int) -> int | None:
        nodes = self._node_service.get_nodes_scheduling_context(col_id)
        today_reviews = self.get_reviews_for_today()
        today_reviews_context = []

        for r in today_reviews:
            node = self._node_service.get_node(r.node_id)

            if not node:
                continue

            today_reviews_context.append(
                ReviewContext(
                    id=r.id,
                    node_type=node.type,
                )
            )
                                
        return self._scheduling_engine.get_next_node(nodes, today_reviews_context)

    def get_next_review(self, col_id: int) -> NodeReview | None:
        next_node_id = self.get_next_review_id(col_id)
        if not next_node_id:
            return None
        node = self._node_service.get_node(next_node_id)
        if not node:
            raise ValueError(f"No node with id {next_node_id}")
        field_value = next(iter(node.content.fields.values()))
        if node.type == NodeType.FRAGMENT:
            return FragmentReview(
                id=next_node_id,
                collection_id=col_id,
                type=node.type,
                content = field_value,
            )
        elif node.type == NodeType.SPORE:
            return SporeReview(
                id=next_node_id,
                collection_id=col_id,
                type=node.type,
                prompt = cloze_to_ellipsis(field_value),
                target = cloze_with_wrapper(field_value, "`", "`"),
                content = field_value,
            )
        else:
            raise ValueError(f"Type {node.type} unknown")
