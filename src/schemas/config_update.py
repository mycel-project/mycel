from pydantic import BaseModel

class ConfigUpdate(BaseModel):
    """
    API schema used to update configuration sections of a collection.

    Attributes:
        collection: Optional updates for collection configuration.
        fsrs: Optional updates for FSRS configuration.
    """
    collection: dict | None = None
    fsrs: dict | None = None
