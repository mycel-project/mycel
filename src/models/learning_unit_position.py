from pydantic.main import BaseModel

from src.models.node_slot_key import NodeSlotKey
    
class LearningUnitPosition(BaseModel):
    node_slot_key: NodeSlotKey
    position: str
