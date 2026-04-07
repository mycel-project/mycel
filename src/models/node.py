from dataclasses import dataclass
from typing import Optional


# type values
NEW        = 0
LEARNING   = 1
REVIEW     = 2
RELEARNING = 3


@dataclass
class Node:
    id: int
    collection_id: int
    type: int
    created_at: int
    updated_at: int
    due: int
    state: int
    content: Optional[dict] = None
    last_review: Optional[int] = None
    stability: Optional[float] = None
    difficulty: Optional[float] = None
    step: Optional[int] = None
    priority: Optional[str] = None
    
