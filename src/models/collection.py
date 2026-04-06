from dataclasses import dataclass


@dataclass
class Collection:
    id: int
    name: str
    created_at: int
    updated_at: int
