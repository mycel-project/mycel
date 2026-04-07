from typing import Optional

from fractional_indexing import generate_key_between, generate_n_keys_between


def insert_between(a_key: Optional[str], b_key: Optional[str]) -> str:
    return generate_key_between(a_key, b_key)


def spread_keys(n: int) -> list[str]:
    """
    Generate n evenly-spaced keys starting from scratch, only when needed
    Might be heavy with a lot of nodes
    """
    if n == 0:
        return []
    return generate_n_keys_between(None, None, n)
