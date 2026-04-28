from pydantic import BaseModel


class SporeReview(BaseModel):
    id: int
    collection_id: int
    type: int
    content: str
