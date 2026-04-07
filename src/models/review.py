from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Review:
    node_id: int
    review_time: int
    rating: int
    review_type: int
    interval: int
    ease: float
    state_before: dict = field(default_factory=dict)
    state_after: dict = field(default_factory=dict)
    id: Optional[int] = None
