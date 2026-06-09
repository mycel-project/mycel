import random

from src.core.lexical_order import LexicalOrder
from src.models.node_slot_key import NodeSlotKey
from src.repositories.learning_unit_repository import LearningUnitRepository
 
 
class PriorityService:
    def __init__(self, learning_unit_repository: LearningUnitRepository, lexical_order: LexicalOrder):
        self._repo = learning_unit_repository
        self._lexical_order = lexical_order
        
    def get_priority(self, collection_id: str, learning_unit_id: str) -> float:
        position = self._repo.get_position(learning_unit_id)
        if position is None:
            raise ValueError(f"{learning_unit_id} not found or has no position")
        return self.position_to_priority(collection_id, position)

    def position_to_priority(self, collection_id: str, position: str) -> float:
        rank = self._repo.count_before_position(collection_id, position)
        total = self._repo.count_by_collection(collection_id)
 
        if total <= 1:
            return 100

        return 100 - (rank / (total - 1)) * 100

    def priority_to_position(self, collection_id: str, percentage: float) -> str:
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")
 
        total = self._repo.count_by_collection(collection_id)
 
        if total == 0:
            return self._lexical_order.insert_between(None, None)

        # two special cases to force insertion at start or at end 
        if percentage == 0:
            tail_key = self._repo.get_tail_key(collection_id)
            return self._lexical_order.insert_between(tail_key, None)
        if percentage == 100:
            head_key = self._repo.get_position_at_offset(collection_id, 0)
            return self._lexical_order.insert_between(None, head_key)
 
        target_index = round(((100 - percentage) / 100) * (total - 1)) 
        target_index = max(0, min(target_index, total - 1))

        left_key = self._repo.get_position_at_offset(collection_id, target_index)
        right_key = self._repo.get_position_at_offset(collection_id, target_index + 1) if target_index + 1 < total else None

        while right_key is not None and left_key == right_key:
            # Handle temporary duplicate positions, e.g. when restoring nodes
            target_index += 1
            right_key = self._repo.get_position_at_offset(collection_id, target_index + 1) if target_index + 1 < total else None

        return self._lexical_order.insert_between(left_key, right_key)

    def get_all_priorities(self, collection_id: str) -> dict[NodeSlotKey, float]:
        total = self._repo.count_by_collection(collection_id)
        if total <= 1:
            return {}
        positions = self._repo.get_all_positions_with_node(collection_id)
        return {
            p.node_slot_key: 100 - (rank / (total - 1)) * 100
            for rank, p in enumerate(positions)
        }

    # May be renamed like "position_random_between_percentage" to explicit that it renders pos
    def prioritise_random_between_percentage(
        self,
        collection_id: str,
        min_percentage: float,
        max_percentage: float,
    ) -> str:
        percentage = random.uniform(min_percentage, max_percentage)
        return self.priority_to_position(collection_id, percentage)
    def prioritise_random_near_priority(
        self,
        collection_id: str,
        priority: float,
        percentage_range: float,
    ) -> str:
        """
        Places a node within a priority window near the given node, sliding the window when close to 100 to avoid accumulation to very high priority.
        Children are placed above source. (more prioritised)
        """
        epsilon = 0.5
        min_pct = min(priority + epsilon, 100 - percentage_range)
        max_pct = min_pct + percentage_range
        return self.prioritise_random_between_percentage(collection_id, min_pct, max_pct)
    

    # Externalize into usecase ?
    def reprioritise_node(self, collection_id: str, learning_unit_id: str, priority: float) -> None:
        new_position = self.priority_to_position(collection_id, priority)
        self._repo.update_position(learning_unit_id, new_position)

    def reindex_all(self, collection_id: str) -> None:
        """
        Rebalances fractional index keys across the entire collection.
    
        Over time, repeated insertions between the same neighbors can produce
        increasingly long keys. This method reassigns evenly spread keys to all
        nodes while preserving their relative order.
        """
        positions = self._repo.get_all_positions(collection_id)
        new_keys = self._lexical_order.spread_keys(len(positions))
        for (node_id, _), new_key in zip(positions, new_keys):
            self._repo.update_position(node_id, new_key)
