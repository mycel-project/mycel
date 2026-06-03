from pydantic import BaseModel, ConfigDict

from src.models.collection_conf import CollectionConf
from src.models.fsrs_conf import FsrsConf


class CollectionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    conf: CollectionConf
    fsrsconf: FsrsConf
    created_at: int
    
