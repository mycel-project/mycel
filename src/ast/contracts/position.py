from pydantic import BaseModel
from .point import Point

class Position(BaseModel):
    start: Point
    end: Point
