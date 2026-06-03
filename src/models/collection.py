from pydantic import BaseModel, ConfigDict
from .collection_conf import CollectionConf
from .fsrs_conf import FsrsConf

class Collection(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: int
    user_id: int
    name: str
    created_at: int
    updated_at: int
    conf: CollectionConf
    fsrsconf: FsrsConf
