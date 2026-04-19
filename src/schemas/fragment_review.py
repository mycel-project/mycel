from pydantic import BaseModel


class FragmentReview(BaseModel):
    id: int
    collection_id: int
    type: int
    content: str
