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
        data: dict,
        tags: list | None = None,
        note_id: int | None = None,
        before_id: int | None = None,
        after_id: int | None = None,
    ) -> Node:
        order_key = self._resolve_position(collection_id, before_id, after_id)
        return self._repo.create(
            collection_id=collection_id,
            data=data,
            tags=tags,
            note_id=note_id,
            order_key=order_key,
        )

    def reprioritise_node(
        self,
        node_id: int,
        new_position_node_id: int | None = None,
    ) -> None:
        if new_position_node_id is None:
            raise ValueError("new_position_node_id is required")
        node = self._repo.get(node_id)
        if node is None:
            raise ValueError(f"Node {node_id} not found")
        new_position_node = self._repo.get(new_position_node_id)
        if new_position_node is None:
            raise ValueError(f"Node {new_position_node_id} not found")
        node_key: str = node.order_key or ""
        target_key: str = new_position_node.order_key or ""
        if not node_key or not target_key:
            raise ValueError("Nodes must have order_key set before reprioritising")

        moving_forward = node_key < target_key

        if moving_forward:
            # Node moves to a higher index: after removing it, the target node
            # shifts one position earlier, so we insert AFTER the target.
            successor_key = self._repo.get_successor_key(
                node.collection_id,
                target_key,
                exclude_id=node_id,
            )
            order_key = insert_between(target_key, successor_key)
        else:
            # Node moves to a lower index: target position is unaffected by the
            # removal, so we insert BEFORE the target.
            predecessor_key = self._repo.get_predecessor_key(
                node.collection_id,
                target_key,
                exclude_id=node_id,
            )
            order_key = insert_between(predecessor_key, target_key)

        self._repo.update_order_key(node_id, order_key)

    def reindex(self, collection_id: int) -> None:
        """Redistribute all order_keys evenly to avoid key bloat."""
        entries = self._repo.get_all_order_keys(collection_id)
        if not entries:
            return
        new_keys = spread_keys(len(entries))
        for (node_id, _), new_key in zip(entries, new_keys):
            self._repo.update_order_key(node_id, new_key)

    def delete_node(self, node_id: int) -> None:
        self._repo.delete(node_id)

    def get_nodes(
        self,
        collection_id: int,
        limit: int,
        after_key: Optional[str] = None,
    ) -> list[NodeListView]:
        nodes = self._repo.get_nodes_after(collection_id, after_key, limit)
        print([node.order_key for node in nodes])
        return [
            NodeListView(
                id=c.id,
                collection_id=c.collection_id,
                type=c.type,
                data=c.data,
                position=i
            )
            for i, c in enumerate(nodes)
        ]
