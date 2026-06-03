from typing import Optional
from pydantic import BaseModel, model_validator

from src.models.collection_conf import CollectionConf
from src.models.algo_conf import AlgoConf


class CollectionUpdate(BaseModel):
    """
    Partial update model for Collection.
    
    Only include fields that you explicitly want to modify.
    Any field provided in this model including fields set to None will be applied and will overwrite the existing value on the collection.

    Fields not included in the update will remain unchanged.
    """
    name: Optional[str] = None
    conf: Optional[CollectionConf] = None
    algoconf: Optional[AlgoConf] = None
