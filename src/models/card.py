from dataclasses import dataclass, field
from typing import Optional


# type values
NEW        = 0
LEARNING   = 1
REVIEW     = 2
RELEARNING = 3


@dataclass
class Card:
    id: int
    collection_id: int
    type: int
    queue: int
    due: int
    interval: int
    ease_factor: float
    reps: int
    lapses: int
    created_at: int
    updated_at: int
    flags: int
    data: dict = field(default_factory=dict)
    tags: list = field(default_factory=list)
    note_id: Optional[int] = None
    last_review: Optional[int] = None
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    fsrs_step: Optional[int] = None
    order_key: Optional[str] = None
    
