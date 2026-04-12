from pydantic import field_validator

from ..contracts import Literal as UnistLiteral

class Literal(UnistLiteral):
    @field_validator("value")
    def check_str(cls, v):
        if not isinstance(v, str):
            raise ValueError("Hast literal must be string")
        return v
