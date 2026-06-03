from pydantic import BaseModel, ConfigDict

from src.models.collection_conf import CollectionConf
from src.models.algo_conf import AlgoConf


class CollectionView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    conf: CollectionConf
    algoconf: AlgoConf
    created_at: int
    
