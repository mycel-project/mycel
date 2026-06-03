from pydantic import BaseModel

class ConfigUpdate(BaseModel): # rename to collection config update i guess
    """
    API schema used to update configuration sections of a collection.

    Attributes:
        collection: Optional updates for collection configuration.
        algo: Optional updates for ALGO configuration.
    """
    collection: dict | None = None
    algo: dict | None = None
