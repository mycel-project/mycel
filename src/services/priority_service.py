from typing import Optional
import random

from fractional_indexing import generate_key_between, generate_n_keys_between
from src.models.node import Node


class PriorityService:
    # need clarification
    def insert_between(self, a_key: Optional[str], b_key: Optional[str]) -> str:
        return generate_key_between(a_key, b_key)

    def spread_keys(self, n: int) -> list[str]:
        if n == 0:
            return []
        return generate_n_keys_between(None, None, n)

    def _sorted_nodes(self, nodes: list[Node]) -> list[Node]:
        return sorted(
            [n for n in nodes if n.priority],
            key=lambda n: n.priority
        )

    def get_nodes_between_percentage(
        self,
        nodes: list[Node],
        min_percentage: float,
        max_percentage: float,
    ) -> list[Node]:

        nodes_sorted = self._sorted_nodes(nodes)
        n = len(nodes_sorted)

        if n == 0:
            return []

        min_index = round((min_percentage / 100) * n)
        max_index = round((max_percentage / 100) * n)

        min_index = max(0, min(min_index, n))
        max_index = max(0, min(max_index, n))

        if min_index > max_index:
            min_index, max_index = max_index, min_index

        if min_index == max_index and min_index < n:
            max_index = min_index + 1

        return nodes_sorted[min_index:max_index]

    def key_to_percentage(self, nodes: list[Node], key: str) -> float:
        nodes_sorted = self._sorted_nodes(nodes)

        if not nodes_sorted:
            return 0.0

        keys = [n.priority for n in nodes_sorted if n.priority]

        extended = sorted(keys + [key])

        index = extended.index(key)

        return (index / (len(extended) - 1)) * 100

    def insert_between_nodes_random(self, nodes: list[Node]) -> str:
        nodes_sorted = self._sorted_nodes(nodes)

        if len(nodes_sorted) < 2:
            raise ValueError("Need at least 2 nodes")

        existing_keys = {n.priority for n in nodes_sorted if n.priority}

        i = random.randint(1, len(nodes_sorted) - 1)

        left_key = nodes_sorted[i - 1].priority
        right_key = nodes_sorted[i].priority

        if not left_key or not right_key:
            raise ValueError("Nodes must have valid priorities")

        new_key = generate_key_between(left_key, right_key)

        while new_key in existing_keys:
            new_key = generate_key_between(left_key, right_key)

        return new_key
