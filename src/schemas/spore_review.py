from pydantic import BaseModel


class SporeReview(BaseModel):
    id: int
    collection_id: int
    type: int
    prompt: str
    target: str
    content: str
