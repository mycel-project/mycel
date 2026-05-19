from pydantic import BaseModel
from datetime import date

from src.types.node_type import NodeType

class CountByTypeAndDay(BaseModel):
    # used to transfer between service/orch, no reale date object
    local_day_midnight_ms: int 
    type: NodeType
    count: int
