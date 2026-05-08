from dataclasses import dataclass
from .collection_conf import CollectionConf
from .fsrs_conf import FsrsConf


@dataclass
class Collection:
    id: int
    user_id: int
    name: str
    created_at: int
    updated_at: int
    conf: CollectionConf
    fsrsconf: FsrsConf
    
