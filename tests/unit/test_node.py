from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.services.node_service import NodeService
from src.services.ressource_service import RessourceService
from src.sources.registry import SourceRegistry
from src.types.node_type import NodeType


def test_create_node(db, col):
    source_registry = SourceRegistry("mycel-test")
    html_to_markdown_registry = HtmlToMdRegistry()

    ressource_service = RessourceService(source_registry, html_to_markdown_registry)
    node_service = NodeService(db, ressource_service)
    node = node_service.create_node(col.id, NodeType.SPORE, {})
    assert type(node.data) == NodeData
    assert type(node.content) == NodeContent
