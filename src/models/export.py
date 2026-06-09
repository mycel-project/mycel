from pydantic import BaseModel
from src.models.learning_unit import LearningUnit
from src.models.user import User
from src.models.collection import Collection
from src.models.node import Node
from src.models.review import Review

class CollectionExport(Collection):
    nodes: list[Node] = []
    learning_units: list[LearningUnit] = []
    reviews: list[Review] = []

class FullExport(BaseModel):
    version: str
    exported_at: str
    user: User
    collections: list[CollectionExport]
