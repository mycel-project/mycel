from typing import cast, Optional
from src.core.node_scheduling_context import NodeSchedulingContext
from src.core.review_context import ReviewContext
from src.types.node_type import NodeType
from src.utils.time import MS_PER_DAY, ms_to_datetime, start_of_day_ms

from collections import Counter
import logging

logger = logging.getLogger(__name__)


class SchedulingEngine:
    def __init__(self):
        self.fragment_vs_spore_proportion = 1/4

    def next_linear_interval(self, node: NodeSchedulingContext) -> int:
        if node.encounter_count is not None:
            return node.encounter_count + 1
        else:
            raise ValueError("No encounter count data for node.")

    def get_next_node(self, nodes: list[NodeSchedulingContext], today_reviews: list[ReviewContext]) -> Optional[int]:
        """
        nodes are already sorted by priority, and filtering by due day keep this priority
        
        return node id
        """
        due_nodes = [n for n in nodes if n.due is not None]
        if not due_nodes:
            return None

        earliest_due = min(due_nodes, key=lambda n: cast(int, n.due))

        day_start = start_of_day_ms(cast(int, earliest_due.due))
        logger.debug(f"Treating day {ms_to_datetime(day_start)}")
        nodes_due_that_day = self.get_node_due_on_day(day_start, due_nodes)

        if not nodes_due_that_day:
            return None

        ratio = self.fragment_spore_ratio(today_reviews)

        requested_type = (
            NodeType.SPORE
            if ratio > self.fragment_vs_spore_proportion
            else NodeType.FRAGMENT
        )

        requested_nodes = [
            n for n in nodes_due_that_day
            if n.type == requested_type.value
        ]

        return (requested_nodes or nodes_due_that_day)[0].id
    

    def fragment_spore_ratio(self, reviews) -> float:
        """
        Compute the ratio between fragment and spore reviews.

        - ratio = fragments / spores
        - Example: 10.0 means 10 fragment reviews per 1 spore review
        - If no spore reviews exist, returns float('inf')
        """
        logger.debug(f"reviews: {reviews}")

        types = [r.node_type for r in reviews]
        counts = Counter(types)

        fragments = counts.get(NodeType.FRAGMENT, 0)
        spores = counts.get(NodeType.SPORE, 0)

        if spores == 0:
            return float("inf") 

        ratio = fragments / spores
        
        logger.debug(f"Fragment/spore ratio: {ratio}")

        return fragments / spores
        

    def get_node_due_on_day(self, day_start: int, nodes: list[NodeSchedulingContext]) -> list[NodeSchedulingContext]:
        """
        day_start in ms timestamp
        """
        day_end = day_start + MS_PER_DAY
        return [
            node for node in nodes
            if node.due is not None and day_start <= node.due < day_end
        ]
