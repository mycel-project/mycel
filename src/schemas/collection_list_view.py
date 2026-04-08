from pydantic import BaseModel


class CollectionListView(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
