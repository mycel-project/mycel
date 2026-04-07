from typing import Optional

from src.db import Db
from src.models.node import Node
from src.repositories.node_repository import NodeRepository
from src.services.ordering_service import insert_between, spread_keys
from src.models.node_list_view import NodeListView


class NodeService:
    """
    Node service logic (higher level than node_repository)
    """
    def __init__(self, db: Db):
        self._repo = NodeRepository(db)

        
    def _resolve_position(
        self,
        collection_id: int,
        before_id: int | None,
        after_id: int | None,
    ) -> str:
        if before_id is None and after_id is None:
            return insert_between(self._repo.get_tail_key(collection_id), None)
        a_key, b_key = self._repo.get_neighbor_keys(collection_id, before_id, after_id)
        return insert_between(a_key, b_key)


    def create_node(
        self,
        collection_id: int,
        content: dict,  # ✅ Accepte un dict
        priority: Optional[str] = None,
    ) -> Node:
        if priority is None:
            priority = self._resolve_position(collection_id, None, None)
        return self._repo.create(
            collection_id=collection_id,
            content=content,
            priority=priority,
        )

    def reprioritise_node(
        self,
        node_id: int,
        new_position_node_id: int,
    ) -> None:
        node = self._repo.get(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found")
        
        new_position_node = self._repo.get(new_position_node_id)
        if new_position_node is None:
            raise ValueError(f"Node {new_position_node_id} not found")
        
        # ✅ Utiliser priority au lieu de order_key
        node_priority = node.priority or ""
        target_priority = new_position_node.priority or ""
        
        if not node_priority or not target_priority:
            raise ValueError("Nodes must have priority set before reprioritising")

        moving_forward = node_priority < target_priority

        if moving_forward:
            successor_priority = self._repo.get_successor_priority(
                node.collection_id,
                target_priority,
                exclude_id=node_id,
            )
            priority = insert_between(target_priority, successor_priority)
        else:
            predecessor_priority = self._repo.get_predecessor_priority(
                node.collection_id,
                target_priority,
                exclude_id=node_id,
            )
            priority = insert_between(predecessor_priority, target_priority)

        self._repo.update_priority(node_id, priority)

    def reindex(self, collection_id: int) -> None:
        """Redistribute all priorities evenly to avoid key bloat."""
        entries = self._repo.get_all_priorities(collection_id)
        if not entries:
            return
        new_keys = spread_keys(len(entries))
        for (node_id, _), new_key in zip(entries, new_keys):
            self._repo.update_priority(node_id, new_key)

    def delete_node(self, node_id: int) -> None:
        """Delete a node"""
        self._repo.delete(node_id)

    def get_nodes(
        self,
        collection_id: int,
        limit: int = 10,
    ) -> list[NodeListView]:
        """Get nodes from a collection with pagination"""
        nodes = self._repo.get_by_collection(collection_id, limit)
        return [
            NodeListView(
                id=n.id,
                collection_id=n.collection_id,
                type=n.type,
                content=n.content,
                position=i
            )
            for i, n in enumerate(nodes)
        ]

    def get_node(self, node_id: int) -> Optional[Node]:
        """Get a single node by ID"""
        return self._repo.get(node_id)

    def get_due_nodes(self, collection_id: int) -> list[Node]:
        """Get nodes that are due for review"""
        return self._repo.get_due(collection_id)

    def update_fsrs_parameters(
        self,
        node_id: int,
        stability: float,
        difficulty: float,
        step: int,
    ) -> None:
        """Update FSRS learning parameters"""
        self._repo.update_fsrs_params(node_id, stability, difficulty, step)

    def mark_reviewed(self, node_id: int) -> None:
        """Mark a node as reviewed"""
        self._repo.update_last_review(node_id)
