from pydantic import Field
from src.models.node import NodeFields
from src.models.node_data import NodeData
from src.schemas.learning_unit_view import LearningUnitView
from src.schemas.node_view import NodeView


class NodeDetailView(NodeView):
    """Full view for single node with all content."""
    fields: NodeFields 
    learning_units: list[LearningUnitView] = Field(default_factory=list)  # 1 for fragment but >=1 for spore
    data: NodeData
