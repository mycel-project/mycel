from pydantic import BaseModel

class DayReviewOverview(BaseModel):
    """
    Not using date object to ease transfer to frontend
    """
    date: str # ISO (2026-01-01)
    due_spores: int = 0
    due_fragments: int = 0
    reviewed_spores: int = 0
    reviewed_fragments: int = 0
