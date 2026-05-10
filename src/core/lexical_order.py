from typing import Optional
 
from fractional_indexing import generate_key_between, generate_n_keys_between
 
 
class LexicalOrder:
    def insert_between(self, a_key: Optional[str], b_key: Optional[str]) -> str:
        return generate_key_between(a_key, b_key)
 
    def spread_keys(self, n: int) -> list[str]:
        if n == 0:
            return []
        return generate_n_keys_between(None, None, n)
 
