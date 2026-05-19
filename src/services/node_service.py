from typing import Optional, Union

from src.core.node_scheduling_context import NodeSchedulingContext
from src.domain.domain_exceptions import NoNodeFound, NodeDeleted
from src.models.node import Node
from src.models.node_data import NodeData
from src.models.type_data import TypeData
from src.repositories.node_repository import NodeRepository
from src.schemas.node_view import NodeView
from src.schemas.node_metrics import NodeMetrics
from src.schemas.node_update import NodeUpdate
from src.models.node_content import NodeContent
from src.types.count_by_type_and_day import CountByTypeAndDay
from src.types.node_type import NodeType
from src.utils.time import overdue_ms, now_ms

class NodeService:
    """
    Default behaviour is to filter nodes by aliveness (deleted_at field at None), excepted in get_node where we raise exception if node is deleted

    No date/datetime object
    """
    def __init__(self, node_repository: NodeRepository):
        self._repo = node_repository
        
    def get_node(self, node_id: int, include_deleted: bool = False) -> Node:
        node = self._repo.get(node_id)
        if node is None:
            raise NoNodeFound(node_id)
        if not include_deleted and node.deleted_at is not None:
            raise NodeDeleted(node_id)
        return node

    def get_nodes(
        self,
        collection_id: int,
        limit: int = 5000,
        include_alive: bool = True,
        include_deleted: bool = False,
    ) -> list[Node]:
        if not include_alive and not include_deleted:
            raise ValueError("At least one of include_alive or include_deleted must be True")
        nodes = self._repo.get_by_collection(collection_id, limit)
        if include_alive and include_deleted:
            return nodes
        if include_alive:
            return self._keep_alive(nodes)
        return self._keep_deleted(nodes)

    def _keep_alive(self, nodes: list[Node]) -> list[Node]:
        return [n for n in nodes if n.deleted_at is None]

    def _keep_deleted(self, nodes: list[Node]) -> list[Node]:
        return [n for n in nodes if n.deleted_at is not None]

    def create_node(
        self,
        collection_id: int,
        type: NodeType,
        content: Union[str, dict, NodeContent],
        position: str, 
        data: Optional[NodeData] = None,
        type_data: Optional[TypeData] = None,
        parent_id: Optional[int] = None,
    ) -> Node:
        node_content = NodeContent.from_input(content)
        return self._repo.create(
            collection_id=collection_id,
            content=node_content,
            type_data=type_data,
            parent_id=parent_id,
            position=position,
            data=data,
            type=type,
        )

    def delete_node(self, node_id: int) -> None:
        self._repo.delete(node_id)

    def restore_node(self, node_id: int) -> Node:
        # Not passing through self.get_node and self.update to not raise NodeDeleted
        node = self._repo.get(node_id)
        if node is None:
            raise NoNodeFound(node_id)
        node.deleted_at = None
        self._repo.update(node)
        return node

    def restore_ancestors(self, node_id: int) -> list[Node]:
        restored = []
        node = self._repo.get(node_id)
        while node is not None and node.parent_id is not None:
            parent = self._repo.get(node.parent_id)
            if parent is None:
                break
            if parent.deleted_at is not None:
                restored.append(self.restore_node(parent.id))
            node = parent
        return restored

    def restore_descendants(self, node_id: int) -> list[Node]:
        children = self._repo.get_children_recursive(node_id)
        restored = []
        for child in children:
            if child.deleted_at is not None:
                restored.append(self.restore_node(child.id))
        return restored

    def soft_delete_node(self, node_id: int) -> Node | None:
        return self.update(node_id, NodeUpdate(
            deleted_at=now_ms()
        ))

    def get_expired_deleted(self, collection_id: int, cutoff_ms: int) -> list[Node]:
        return self._repo.get_expired_deleted(collection_id, cutoff_ms)

    def soft_delete_subtree(self, node_id: int) -> list[int]:
        subtree = self.get_subtree(node_id)
        ids = [n.id for n in subtree]
        for node_id in ids:
            try: 
                self.soft_delete_node(node_id)
            except NodeDeleted: # If node in subtree is already soft deleted, nothing more to do
                continue
        return ids

    def get_nodes_scheduling_context(self, collection_id: int) -> list[NodeSchedulingContext]:
        nodes = self.get_nodes(collection_id)
        now = now_ms()
        return [
            NodeSchedulingContext(
                id=n.id,
                type=n.type,
                position=n.position, 
                parent_id=n.parent_id,
                due=n.due,
                last_review=n.last_review,
                type_data=n.type_data,
                overdue=overdue_ms(n.due, now)
            )
            for n in nodes
        ]
    
    def get_deleted_nodes_view(
        self,
        collection_id: int,
    ) -> list[NodeView]:
        nodes = self.get_nodes(collection_id, include_alive=False, include_deleted=True)
        return [
            self.node_to_view(n, i)
            for i, n in enumerate(nodes)
        ]

    def node_to_view(self, node: Node, priority: int) -> NodeView:
        return NodeView(
            id=node.id,
            collection_id=node.collection_id,
            type=node.type,
            content=node.content,
            priority=priority,
            parent_id=node.parent_id,
            due=node.due,
            data=node.data,
            deleted_at=node.deleted_at,
            type_data=node.type_data if node.type == NodeType.FRAGMENT else None # Can be made more specific if needed, to select specific data depending on the node type. At the moment, only fragment type_data is used by frontend.
        )

    def get_children_recursive(self, node_id: int) -> list[Node]: # Rename to descendants?
        self.get_node(node_id)  # To check node validity
        return self._repo.get_children_recursive(node_id)

    def get_subtree(self, node_id: int) -> list[Node]:
        root = self.get_node(node_id)
        return [root] + self.get_children_recursive(node_id)

    def delete_subtree(self, node_id: int) -> list[int]:
        subtree = self.get_subtree(node_id)
        ids = [n.id for n in subtree]
        for node_id in ids:
            self._repo.delete(node_id)
        return ids

    def get_root_node(self, node_id: int) -> Node:
        root_id = self.get_root_id(node_id)
        return self.get_node(root_id)
        
    def get_root_id(self, node_id: int) -> int:
        current_id = node_id

        while True:
            node = self.get_node(current_id)

            if node.parent_id is None:
                return node.id

            current_id = node.parent_id

    def get_node_metrics(self, node_id: int) -> Optional[NodeMetrics]:
        node = self.get_node(node_id)
        return NodeMetrics(
            id=node.id,
            last_review=node.last_review,
            type_data=node.type_data
        )

    def get_node_extanded(self, node_id: int) -> dict:
        node_view = self.get_node(node_id)
        node_metrics = self.get_node_metrics(node_id)
        return {"view": node_view, "metrics": node_metrics}

    def update_position(self, node_id: int, position: str):
        self.update(node_id, NodeUpdate(position=position))

    def update(self, node_id: int, updates: NodeUpdate, include_deleted = False) -> Node:
        node = self.get_node(node_id, include_deleted)
        print("before_update: ", node)
        print("update: ", updates)
        
        # Fields explicitly provided in updates (even if set to None) will overwrite existing values (due to model_fiels_set).
        # To prevent setting a field to None,y do not include it in the update payload.
        for field in updates.model_fields_set: 
            value = getattr(updates, field)
            setattr(node, field, value)

        self._repo.update(node)
        return node
        
    def get_due_nodes(self, collection_id: int) -> list[Node]:
        return self._keep_alive(self._repo.get_due(collection_id))

    def get_due_count_by_type_and_day(
        self,
        collection_id: int,
        start_ms: Optional[int] = None,
        to_ms: Optional[int] = None,
        tz_offset_minutes: int = 0,
    ) -> list[CountByTypeAndDay]:
        # Note that countByTypeAndDay is not specifc do DUE nodes.
        
        if start_ms is None:
            start_ms = 0
        if to_ms is None:
            to_ms = 2**63 - 1
        raw = self._repo.due_count_by_type_and_day(collection_id, start_ms, to_ms, tz_offset_minutes)
        return [
            CountByTypeAndDay(
                local_day_midnight_ms=day,
                type=NodeType(type),
                count=count
            )
            for day, type, count in raw
        ]
