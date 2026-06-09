from pydantic.main import BaseModel


class NodeSlotPriority(BaseModel):
    node_id: str
    slot: int
    priority: float
