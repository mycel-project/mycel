import json

from pydantic import BaseModel, ConfigDict
from .collection_conf import CollectionConf
from .algo_conf import AlgoConf

class Collection(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    id: str
    user_id: str
    name: str
    created_at: int
    updated_at: int
    conf: CollectionConf
    algoconf: AlgoConf

    @classmethod
    def from_db(cls, row: dict) -> 'Collection':
        row_dict = dict(row) if hasattr(row, 'keys') else row.__dict__
        
        raw_conf = row_dict["conf"]
        parsed_conf = json.loads(raw_conf) if isinstance(raw_conf, str) else raw_conf
        
        raw_algo = row_dict["algoconf"]
        parsed_algo = json.loads(raw_algo) if isinstance(raw_algo, str) else raw_algo

        return cls(
            id=row_dict["id"],
            user_id=row_dict["user_id"],
            name=row_dict["name"],
            created_at=row_dict["created_at"],
            updated_at=row_dict["updated_at"],
            conf=CollectionConf.model_validate(parsed_conf),
            algoconf=AlgoConf.model_validate(parsed_algo),
        )
