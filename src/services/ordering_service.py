from typing import Optional

from fractional_indexing import generate_key_between

def insert_between(a_key: Optional[str], b_key: Optional[str]) -> str:
    return generate_key_between(a_key, b_key)
