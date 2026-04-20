from typing import Optional, Union

from src.core.node_scheduling_context import NodeSchedulingContext
from src.db import Db
from src.models.node import Node
from src.models.node_data import NodeData
from src.models.type_data import TypeData
from src.repositories.node_repository import NodeRepository
from src.services.node_format_service import NodeFormatService
from src.services.priority_service import PriorityService
from src.schemas.node_view import NodeView
from src.schemas.node_metrics import NodeMetrics
from src.schemas.node_update import NodeUpdate
from src.models.node_content import NodeContent
from src.services.ressource_service import RessourceService
from src.types.node_type import NodeType
from src.utils.time import overdue_ms, now_ms
from src.utils.url import is_valid_url

class NodeService:
    """
    Node service logic (higher level than node_repository)
    """
    def __init__(self, db: Db, ressource_service: RessourceService, priority_service: PriorityService):
        self._repo = NodeRepository(db)
        self._ressource_service = ressource_service
        self._priority_service = priority_service

    def reindex_all(self, collection_id: int) -> None:
        nodes = self._repo.get_by_collection(collection_id)
        nodes = sorted(nodes, key=lambda n: n.priority or "")
        new_keys = self._priority_service.spread_keys(len(nodes))
        for node, new_key in zip(nodes, new_keys):
            self._repo.update_priority(node.id, new_key)

    def _resolve_position(
            self,
            collection_id: int,
            before_id: int | None,
            after_id: int | None,
    ) -> str:

        if before_id is None and after_id is None:
            tail_key = self._repo.get_tail_key(collection_id)
            return self._priority_service.insert_between(tail_key, None)

        a_key, b_key = self._repo.get_neighbor_keys(collection_id, before_id, after_id)
        return self._priority_service.insert_between(a_key, b_key)

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
            priority = self._priority_service.insert_between(target_priority, successor_priority)
        else:
            predecessor_priority = self._repo.get_predecessor_priority(
                node.collection_id,
                target_priority,
                exclude_id=node_id,
            )
            
            priority = self._priority_service.insert_between(predecessor_priority, target_priority)

        self._repo.update_priority(node_id, priority)


    def prioritise_random_between_percentage(
            self,
            collection_id: int,
            min_percentage: int,
            max_percentage: int,
    ) -> str:

        nodes = self._repo.get_by_collection(collection_id)

        slice_nodes = self._priority_service.get_nodes_between_percentage(
            nodes,
            min_percentage,
            max_percentage,
        )

        if not slice_nodes:
            raise ValueError("No nodes in range")

        return self._priority_service.insert_between_nodes_random(slice_nodes)

    def prioritise_random_behind_node(
        self,
        collection_id: int,
        node_id: int,
        percentage_range: int,
    ) -> str:
        nodes = self._repo.get_by_collection(collection_id)

        front_node = self.get_node(node_id)
        if front_node is None:
            raise ValueError(f"No node with id {node_id}.")

        front_pct = self._priority_service.key_to_percentage(
            nodes,
            front_node.priority
        )

        min_front_pct = 100 - percentage_range
        if front_pct > min_front_pct:
            front_pct = min_front_pct

        start = front_pct
        end = min(100, start + percentage_range)

        slice_nodes = self._priority_service.get_nodes_between_percentage(
            nodes,
            start,
            end,
        )

        step = max(1, percentage_range // 5)

        while len(slice_nodes) < 2 and end < 100:
            end = min(100, end + step)
            slice_nodes = self._priority_service.get_nodes_between_percentage(
                nodes,
                start,
                end,
            )

        if len(slice_nodes) < 2:
            front_pct = max(0, front_pct - percentage_range)
            start = front_pct
            end = min(100, start + percentage_range)

            slice_nodes = self._priority_service.get_nodes_between_percentage(
                nodes,
                start,
                end,
            )

            while len(slice_nodes) < 2 and start > 0:
                start = max(0, start - step)
                slice_nodes = self._priority_service.get_nodes_between_percentage(
                    nodes,
                    start,
                    end,
                )

        if len(slice_nodes) < 2:
            raise ValueError("Not enough nodes in range for insertion")

        return self._priority_service.insert_between_nodes_random(slice_nodes)
    
    def create_node (
        self,
        collection_id: int,
        type: NodeType,
        content: Union[str, dict, NodeContent],
        data: Optional[NodeData] = None,
        type_data: Optional[TypeData] = None,
        parent_id: Optional[int] = None,
        priority: Optional[str] = None,
    ) -> Node:
        if priority is None:
            if parent_id is None:  # New nodes without a parent are given high priority
                priority = self.prioritise_random_between_percentage(collection_id, 5, 15)
            else:
                priority = self.prioritise_random_behind_node(collection_id, parent_id, 10)
        node_content = NodeContent.from_input(content)
        return self._repo.create(
            collection_id=collection_id,
            content=node_content,
            type_data=type_data,
            parent_id=parent_id,
            priority=priority,
            data=data,
            type=type,
        )

    
    def create_node_from_url(
        self,
        collection_id: int,
        url: str,
    ) -> Node:
        valid_url = is_valid_url(url)
        if not valid_url:
            raise ValueError("Invalid URL")
        ressource = self._ressource_service.get_ressource_from_url(url)
        return self.create_node(
            collection_id=collection_id,
            content=NodeContent.from_input(ressource.content),
            data=NodeData(title=ressource.title, src=ressource.source),
            type=NodeType.FRAGMENT
        )

    def delete_node(self, node_id: int) -> None:
        """Delete a node"""
        self._repo.delete(node_id)

    def get_nodes_scheduling_context(self, collection_id: int) -> list[NodeSchedulingContext]:
        nodes = self.get_raw_nodes(collection_id)
        now = now_ms()
        return [
            NodeSchedulingContext(
                id=n.id,
                type=n.type,
                priority=n.priority, 
                parent_id=n.parent_id,
                due=n.due,
                last_review=n.last_review,
                type_data=n.type_data,
                overdue=overdue_ms(n.due, now)
            )
            for n in nodes
        ]

    def get_raw_nodes(self, collection_id: int) -> list[Node]:
        return self._repo.get_by_collection(collection_id)

    def get_nodes(
        self,
        collection_id: int,
        limit: int = 100,
    ) -> list[NodeView]:
        nodes = self._repo.get_by_collection(collection_id, limit)
        return [
            NodeView(
                id=n.id,
                collection_id=n.collection_id,
                type=n.type,
                content=n.content.model_dump(),
                position=i,
                parent_id=n.parent_id,
                due=n.due,
                data=n.data.model_dump()
            )
            for i, n in enumerate(nodes)
        ]

    def get_node(self, node_id: int) -> Optional[Node]:
        return self._repo.get(node_id)

    def get_node_metrics(self, node_id: int) -> Optional[NodeMetrics]:
        n = self._repo.get(node_id)
        if not n:
            return
        return NodeMetrics(
            id=n.id,
            last_review=n.last_review,
            type_data=n.type_data
        )

    def get_node_extanded(self, node_id: int) -> dict:
        node_view = self.get_node(node_id)
        node_metrics = self.get_node_metrics(node_id)
        return {"view": node_view, "metrics": node_metrics}

    def update(self, node_id: int, updates: NodeUpdate) -> None:
        node = self._repo.get(node_id)

        if node is None:
            raise ValueError(f"Node {node_id} not found")
        
        for field, value in updates:
            if value is not None:
                setattr(node, field, value)

        self._repo.update(node)

    def get_due_nodes(self, collection_id: int) -> list[Node]:
        return self._repo.get_due(collection_id)
