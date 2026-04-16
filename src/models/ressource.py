from pydantic import BaseModel

class Ressource(BaseModel):
    title: str | None
    content: str
    source: str
