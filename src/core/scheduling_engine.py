import math

from typing import cast, Optional
from src.core.node_scheduling_context import NodeSchedulingContext
from src.core.review_context import ReviewContext
from src.types.node_type import NodeType
from src.utils.time import MS_PER_DAY, ms_to_datetime, now_ms, start_of_local_day_ms

from collections import Counter
import logging

logger = logging.getLogger(__name__)


class SchedulingEngine:
    def __init__(self):
        # Need instanciation from user config
        self.fragment_vs_spore_proportion = 1/4
        self.fragment_rep_mult = 1.5
        self.fragment_depth_midpoint = 4.0

    def compute_fragment_next_interval(self, depth, rep_index) -> int:
        """
        Computes the interval in days before the next review of a fragment.

        Deeper fragments grow faster toward long intervals (exponential growth),
        while shallow fragments stay closer to a linear, regular review pace.
        The transition between linear and exponential behavior is controlled by depth_midpoint.

        depth: depth in the node tree (0 = root, 1 = first child, ...)
        rep_index: repetition index (0 = creation, 1 = first review, ...)
        fragment_rep_mult: how aggressively intervals grow for deep fragments
        fragment_depth_midpoint: nesting level at which growth is halfway between linear and exponential

        returns interval in days (capped at 365).
        """
        initial = min(1 + depth * 2, 15) # initial value at creation clamped 
        exp_weight = 1 - math.exp(-depth / self.fragment_depth_midpoint)
        interval = initial
        for _ in range(rep_index):
            additive_step = initial
            multiplicative_step = interval * (self.fragment_rep_mult - 1)
            step = additive_step * (1 - exp_weight) + multiplicative_step * exp_weight
            interval = int(min(interval + step, 365))
        return interval

    def next_linear_interval(self, node: NodeSchedulingContext) -> int:
        if node.encounter_count is not None:
            return node.encounter_count + 1
        else:
            raise ValueError("No encounter count data for node.")

    def get_next_node(
        self,
        nodes: list[NodeSchedulingContext],
        today_reviews: list[ReviewContext],
        tz_offset_minutes: int = 0,
    ) -> Optional[int]:
        """
        nodes are already sorted by priority, and filtering by due day keep this priority

        Nodes are filtered to those due today (in the user's local timezone), then split into ready (due timestamp already passed) and not_yet. Not_yet nodes only surface when nothing ready remains: this prevents a freshly-reviewed spore fromreappearing immediately just because it falls within the current day. The spore/fragment ratio is then applied to balance the session.
        
        return node id
        """
        due_nodes = [
            n for n in nodes
            if n.due is not None
            and not (n.type == NodeType.FRAGMENT and getattr(n.type_data, 'dismiss', False))
        ]

        if not due_nodes:
            return None

        earliest_due = min(due_nodes, key=lambda n: cast(int, n.due))

        day_start = start_of_local_day_ms(cast(int, earliest_due.due), tz_offset_minutes)
        if day_start > now_ms():
            # No more reviews
            return None
        logger.debug(f"Treating day {ms_to_datetime(day_start)}")
        nodes_due_that_day = self.get_node_due_on_day(day_start, due_nodes)

        if not nodes_due_that_day:
            return None

        now = now_ms()
        ready = [n for n in nodes_due_that_day if n.due <= now]
        not_yet = [n for n in nodes_due_that_day if n.due > now]

        pool = ready or not_yet

        ratio = self.fragment_spore_ratio(today_reviews)

        requested_type = (
            NodeType.SPORE
            if ratio > self.fragment_vs_spore_proportion
            else NodeType.FRAGMENT
        )

        requested_nodes = [
            n for n in pool
            if n.type == requested_type.value
        ]

        return (requested_nodes or pool)[0].id
    

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
