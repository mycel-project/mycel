from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NodeListView:
    id: int
    collection_id: int
    type: int
    content: dict | None
    position: int
