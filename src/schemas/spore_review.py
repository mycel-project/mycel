from pydantic import BaseModel


class SporeReview(BaseModel):
    id: str
    collection_id: str
    type: int
    content: str
