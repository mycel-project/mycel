from pydantic import BaseModel, Field

class CollectionConf(BaseModel):
    theme: str = Field(default="light")
