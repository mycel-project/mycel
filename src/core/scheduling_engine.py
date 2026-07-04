import math

from typing import cast, Optional
from src.core.review_context import ReviewContext
from src.core.scheduling_context import SchedulingContext
from src.models.node import NodeType
from src.services.user_service import UserService
from src.utils.time import MS_PER_DAY, ms_to_datetime, now_ms, start_of_local_day_ms

from collections import Counter
import logging

logger = logging.getLogger(__name__)


class SchedulingEngine:
    def __init__(self, user_service: UserService):
        # Need instanciation from user config
        self.fragment_vs_spore_proportion = 1/4
        self.fragment_rep_mult = 1.5
        self.fragment_depth_midpoint = 4.0
        self.user_service = user_service

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

    def get_due_lu(self, learning_units: list[SchedulingContext]):
        return [
            lu for lu in learning_units
            if lu.due is not None
            and not (lu.type == NodeType.FRAGMENT and getattr(lu, 'dismiss', False))
        ]

    def get_next_learning_unit_id(
        self,
        user_id: str,
        learning_units: list[SchedulingContext],
        today_reviews: list[ReviewContext],
        tz_offset_minutes: int = 0,
    ) -> Optional[str]:
        """
        units are already sorted by priority, and filtering by due day keep this priority

        Units are filtered to those due today (in the user's local timezone), then split into ready (due timestamp already passed) and not_yet. Not_yet nodes only surface when nothing ready remains: this prevents a freshly-reviewed spore fromreappearing immediately just because it falls within the current day. The spore/fragment ratio is then applied to balance the session.
        
        return node id
        """
        due = self.get_due_lu(learning_units)

        if not due:
            return None

        earliest_due = min(due, key=lambda lu: cast(int, lu.due))

        day_start = start_of_local_day_ms(cast(int, earliest_due.due), tz_offset_minutes)
        if day_start > now_ms():
            # No more reviews
            return None
        logger.debug(f"Treating day {ms_to_datetime(day_start)}")
        due_that_day = self.get_due_on_day(day_start, due)

        if not due_that_day:
            return None

        now = now_ms()
        if self.user_service.get_wait_for_due_time(user_id):
            ready = [lu for lu in due_that_day if lu.due <= now]
            pool = ready or due_that_day
        else:
            pool = due_that_day

        ratio = self.fragment_spore_ratio(today_reviews)

        requested_type = (
            NodeType.SPORE
            if ratio > self.fragment_vs_spore_proportion
            else NodeType.FRAGMENT
        )

        requested_learning_units = [
            lu for lu in pool
            if lu.type == requested_type.value
        ]

        return (requested_learning_units or pool)[0].id
    

    def fragment_spore_ratio(self, reviews: list[ReviewContext]) -> float:
        """
        Compute the ratio between fragment and spore reviews.

        - ratio = fragments / spores
        - Example: 10.0 means 10 fragment reviews per 1 spore review
        - If no spore reviews exist, returns float('inf')
        """
        logger.debug(f"reviews: {reviews}")

        types = [r.learning_unit_type for r in reviews]
        counts = Counter(types)

        fragments = counts.get(NodeType.FRAGMENT, 0)
        spores = counts.get(NodeType.SPORE, 0)

        if spores == 0:
            return float("inf") 

        ratio = fragments / spores
        
        logger.debug(f"Fragment/spore ratio: {ratio}")

        return fragments / spores
        

    def get_due_on_day(self, day_start: int, learning_units: list[SchedulingContext]) -> list[SchedulingContext]:
        """
        day_start in ms timestamp
        """
        day_end = day_start + MS_PER_DAY
        return [
            lu for lu in learning_units
            if lu.due is not None and day_start <= lu.due < day_end
        ]
