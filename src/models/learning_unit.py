import json
from typing import Annotated, Any

from pydantic import Field, RootModel, field_validator

from src.models.fragment import Fragment
from src.models.spore import Spore


class LearningUnit(RootModel):
    root: Annotated[Fragment | Spore, Field(discriminator="type")]

    @property
    def id(self): return self.root.id
    @property
    def node_id(self): return self.root.node_id
    @property
    def type(self): return self.root.type
    @property
    def position(self): return self.root.position
    @property
    def due(self): return self.root.due
    @property
    def last_review(self): return self.root.last_review

    @field_validator("root", mode="before")
    @classmethod
    def prepare_data(cls, v: Any) -> Any:
        if isinstance(v, dict):
            # Si on reçoit la ligne brute de la DB (avec unit_data)
            if "unit_data" in v:
                data = v.copy()
                unit_data = json.loads(data.pop("unit_data", "{}"))
                # On remonte les champs et on normalise le type
                return {
                    "id": data.get("id"),
                    "node_id": data.get("node_id"),
                    "position": data.get("position"),
                    "due": data.get("due"),
                    "last_review": data.get("last_review"),
                    "type": data.get("unit_type"),
                    **unit_data
                }
        return v
