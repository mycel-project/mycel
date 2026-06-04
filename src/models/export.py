from pydantic import BaseModel
from src.models.user import User
from src.models.collection import Collection
from src.models.node import Node
from src.models.review import Review

class CollectionExport(Collection):
    nodes: list[Node] = []
    reviews: list[Review] = []

class FullExport(BaseModel):
    version: str
    exported_at: int
    user: User
    collections: list[CollectionExport]
