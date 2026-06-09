from typing import Optional
from collections import defaultdict

from src.core.scheduling_context import SchedulingContext
from src.domain.domain_exceptions import NoLearningUnitFound, NoNodeFound, NodeDeleted
from src.models.learning_unit import LearningUnit
from src.models.node import Node, NodeFields, NodeStatus, NodeType
from src.models.node_data import NodeData
from src.repositories.learning_unit_repository import LearningUnitRepository
from src.repositories.node_repository import NodeRepository
from src.schemas.node_view import NodeView
from src.schemas.node_update import NodeUpdate
from src.types.count_by_type_and_day import CountByTypeAndDay
from src.utils.time import overdue_ms, now_ms

class NodeService:
    """
    Default behaviour is to filter nodes by aliveness (deleted_at field at None), excepted in get_node where we raise exception if node is deleted

    No date/datetime object
    """
    def __init__(self, node_repository: NodeRepository, learning_unit_repository: LearningUnitRepository):
        self._node_repo = node_repository
        self._lu_repo = learning_unit_repository

    def _hydrate_nodes(self, nodes: list[Node]) -> None:
        # staying hydrated throughout the day is essential!
        if not nodes:
            return
        
        node_ids = [n.id for n in nodes]
        all_units = self._lu_repo.get_by_nodes(node_ids)

        units_by_node = defaultdict(list)
        for unit in all_units:
            units_by_node[unit.node_id].append(unit)

        for node in nodes:
            node.learning_units = units_by_node[node.id]        

    def get_node(self, node_id: str, include_deleted: bool = False) -> Node:
        node = self._node_repo.get(node_id)
        if node is None:
            raise NoNodeFound(node_id)
        if not include_deleted and node.deleted_at is not None:
            raise NodeDeleted(node_id)
        self._hydrate_nodes([node])
        return node

    def get_node_from_learning_unit(self, learning_unit_id: str) -> Node:
        unit = self._lu_repo.get(learning_unit_id)
        if unit is None:
            raise NoNodeFound(learning_unit_id)
        return self.get_node(unit.node_id)

    def get_learning_unit(self, learning_unit_id: str, include_deleted: bool = False) -> LearningUnit:
        unit = self._lu_repo.get(learning_unit_id)
        if unit is None:
            raise NoLearningUnitFound(learning_unit_id)
        self.get_node(unit.node_id, include_deleted)
        return unit

    def get_node_for_user(self, user_id: str, col_id: str, node_id: str, include_deleted: bool = False) -> Node:
        node = self._node_repo.get_owned(user_id, col_id, node_id)
        if node is None:
            raise NoNodeFound(node_id)
        if not include_deleted and node.deleted_at is not None:
            raise NodeDeleted(node_id)
        self._hydrate_nodes([node])
        return node

    def get_nodes(
        self,
        user_id: str,
        collection_id: str,
        limit: int = 5000,
        include_alive: bool = True,
        include_deleted: bool = False,
    ) -> list[Node]:
        if not include_alive and not include_deleted:
            raise ValueError("At least one of include_alive or include_deleted must be True")
        nodes = self._node_repo.get_by_collection(collection_id, limit)
        if include_alive and include_deleted:
            filtered_nodes = nodes
        elif include_alive:
            filtered_nodes = self._keep_alive(nodes)
        else:
            filtered_nodes = self._keep_deleted(nodes)

        self._hydrate_nodes(filtered_nodes)
        return filtered_nodes
    
    def _keep_alive(self, nodes: list[Node]) -> list[Node]:
        return [n for n in nodes if n.deleted_at is None]

    def _keep_deleted(self, nodes: list[Node]) -> list[Node]:
        return [n for n in nodes if n.deleted_at is not None]

    def create_node(
        self,
        user_id: str,
        collection_id: str,
        template_id: str,
        type: NodeType,
        fields: NodeFields,
        learning_unit: LearningUnit, # cannot create a node without learning unit for now
        data: Optional[NodeData] = None,
        status: NodeStatus = NodeStatus.ACTIVE,
        parent_id: Optional[str] = None,
    ) -> Node:
        node = self._node_repo.create(
            collection_id=collection_id,
            template_id=template_id,
            base_for=type,
            fields=fields,
            data=data,
            status=status,
            parent_id=parent_id,
        )
        learning_unit.node_id = node.id 
        self._lu_repo.create(learning_unit)
        
        self._hydrate_nodes([node])
        return node

    def delete_node(self, node_id: str) -> None:
        self._node_repo.delete(node_id)

    def restore_node(self, node_id: str) -> Node:
        node = self.get_node(node_id, True)
        self.update(node.id, NodeUpdate(deleted_at=None), True)
        return node

    def restore_ancestors(self, node_id: str) -> list[Node]:
        restored = []
        node = self.get_node(node_id)
        while node is not None and node.parent_id is not None:
            parent = self.get_node(node.parent_id, True)
            if parent is None:
                break
            if parent.deleted_at is not None:
                restored.append(self.restore_node(parent.id))
            node = parent
        self._hydrate_nodes(restored)
        return restored

    def restore_descendants(self, node_id: str) -> list[Node]:
        children = self._node_repo.get_children_recursive(node_id)
        restored = []
        for child in children:
            if child.deleted_at is not None:
                restored.append(self.restore_node(child.id))
        self._hydrate_nodes(restored)
        return restored

    def soft_delete_node(self, node_id: str) -> Node | None:
        return self.update(node_id, NodeUpdate(
            deleted_at=now_ms()
        ))

    def get_expired_deleted(self, collection_id: str, cutoff_ms: int) -> list[Node]:
        nodes = self._node_repo.get_expired_deleted(collection_id, cutoff_ms)
        self._hydrate_nodes(nodes)
        return nodes

    def soft_delete_subtree(self, node_id: str) -> list[str]:
        subtree = self.get_subtree(node_id)
        ids = [n.id for n in subtree]
        for node_id in ids:
            try: 
                self.soft_delete_node(node_id)
            except NodeDeleted: # If node in subtree is already soft deleted, nothing more to do
                continue
        return ids

    def get_scheduling_context(self, user_id: str, collection_id: str) -> list[SchedulingContext]:
            nodes = self.get_nodes(user_id, collection_id)
            now = now_ms()

            return [
                SchedulingContext(
                    id=n.id,  
                    type=n.base_for,
                    position=u.position, 
                    parent_id=n.parent_id,
                    due=u.due,            
                    last_review=u.last_review, 
                    overdue=overdue_ms(u.due, now)
                )
                for n in nodes
                for u in n.learning_units
            ]
    
    def node_to_view(self, node: Node, priorities: list[float], preview: str) -> NodeView:
        return NodeView(
            id=node.id,
            collection_id=node.collection_id,
            template_id=node.template_id,
            parent_id=node.parent_id,
            type=node.base_for,
            status=node.status,
            updated_at=node.updated_at,
            created_at=node.created_at,
            deleted_at=node.deleted_at,
            content_preview=preview,
            dues=[u.due for u in node.learning_units if u.due is not None],
            priorities=priorities,
        )

    def get_depth(self, node_id: str) -> int:
        depth = 0
        current_id = node_id
        while True:
            node = self.get_node(current_id)
            if node.parent_id is None:
                return depth
            current_id = node.parent_id
            depth += 1

    def get_children_recursive(self, node_id: str) -> list[Node]: # Rename to descendants?
        self.get_node(node_id)
        nodes = self._node_repo.get_children_recursive(node_id)
        self._hydrate_nodes(nodes)
        return nodes

    def get_subtree(self, node_id: str) -> list[Node]:
        root = self.get_node(node_id)
        self._hydrate_nodes([root])
        return [root] + self.get_children_recursive(node_id)

    def delete_subtree(self, node_id: str) -> list[str]:
        subtree = self.get_subtree(node_id)
        ids = [n.id for n in subtree]
        for node_id in ids:
            self._node_repo.delete(node_id)
        return ids

    def get_root_node(self, node_id: str) -> Node:
        root_id = self.get_root_id(node_id)
        return self.get_node(root_id)
        
    def get_root_id(self, node_id: str) -> str:
        current_id = node_id

        while True:
            node = self.get_node(current_id)

            if node.parent_id is None:
                return node.id

            current_id = node.parent_id

    def update_learning_unit(self, learning_unit: LearningUnit) -> LearningUnit | None:
        """
        Full replacement update: no partial update model for now due to Fragment/Spore inheritance complexity.
        """
        # Could add a flag to update node updated_at when updating learning unit?
        return self._lu_repo.update(learning_unit)

    def update_position(self, learning_unit_id: str, position: str) -> None:
        self._lu_repo.update_position(learning_unit_id, position)

    def update(self, node_id: str, updates: NodeUpdate, include_deleted = False) -> Node:
        node = self.get_node(node_id, include_deleted)
        print("before_update: ", node)
        print("update: ", updates)
        
        # Fields explicitly provided in updates (even if set to None) will overwrite existing values (due to model_fiels_set).
        # To prevent setting a field to None, do not include it in the update payload.
        for field in updates.model_fields_set: 
            value = getattr(updates, field)
            setattr(node, field, value)

        self._node_repo.update(node)
        self._hydrate_nodes([node])
        return node
        
    # def get_due_nodes(self, collection_id: str) -> list[Node]: # unused?
    #     return self._keep_alive(self._repo.get_dues(collection_id))

    def get_due_count_by_type_and_day(
        self,
        collection_id: str,
        start_ms: Optional[int] = None,
        to_ms: Optional[int] = None,
        tz_offset_minutes: int = 0,
    ) -> list[CountByTypeAndDay]:
        # Note that countByTypeAndDay is not specifc do DUE nodes.
        
        if start_ms is None:
            start_ms = 0
        if to_ms is None:
            to_ms = 2**63 - 1
        raw = self._lu_repo.due_count_by_type_and_day(collection_id, start_ms, to_ms, tz_offset_minutes)
        return [
            CountByTypeAndDay(
                local_day_midnight_ms=day,
                type=NodeType(type),
                count=count
            )
            for day, type, count in raw
        ]
