from pydantic import BaseModel, Field

class CollectionConfUpdate(BaseModel):
    theme: str | None = Field(default=None)
