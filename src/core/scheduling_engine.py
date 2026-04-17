from src.core.node_scheduling_context import NodeSchedulingContext


class SchedulingEngine:
    def __init__(self):
        pass

    def get_next_card(self, nodes: list[NodeSchedulingContext]) -> int:
        """
        return node id
        """
        valid_nodes = [n for n in nodes if n.due is not None]

        if not valid_nodes:
            raise ValueError("No nodes with due date")

        next_node = min(valid_nodes, key=lambda n: n.due)

        return next_node.id
