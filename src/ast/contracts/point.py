from pydantic import BaseModel, Field


class Point(BaseModel):
    line: int = Field(ge=1)
    column: int = Field(ge=1)
    offset: int | None = Field(default=None, ge=0)
