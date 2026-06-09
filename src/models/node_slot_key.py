from pydantic.config import ConfigDict
from pydantic.main import BaseModel

class NodeSlotKey(BaseModel):
    model_config = ConfigDict(frozen=True)
    node_id: str
    slot: int = 0
