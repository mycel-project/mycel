from pydantic import BaseModel


class OutlineEntry(BaseModel):
    level: int
    title: str
    offset: int # In char 

class Outline(BaseModel):
    entries: list[OutlineEntry]
