from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.core.scheduling_engine import SchedulingEngine
from src.services.collection_service import CollectionService
from src.services.fsrs_service import FsrsService
from src.services.node_service import NodeService
from src.services.ressource_service import RessourceService
from src.services.review_service import ReviewService
from src.sources.registry import SourceRegistry
from tests.utils.debug_nodes import print_nodes


def test_review_node(db, col, nodes):
    print_nodes(nodes)
    engine = SchedulingEngine()
    source_registry = SourceRegistry("mycel-test")
    html_to_markdown_registry = HtmlToMdRegistry()

    ressource_service = RessourceService(source_registry, html_to_markdown_registry)
    node_service = NodeService(db, ressource_service)
    
    collection_service = CollectionService(db)
    fsrs_service = FsrsService(collection_service, node_service)
    review_service = ReviewService(db, engine, fsrs_service, node_service)

    print()
    print(node_service.get_node(review_service.get_next_review(col.id)))
