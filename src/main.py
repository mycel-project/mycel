import asyncio
import json

from pathlib import Path

from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.core.app_infos import AppInfos
from src.core.lexical_order import LexicalOrder
from src.db import Db
from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.domain.create_node_from_url_usecase import CreateNodeFromUrlUseCase
from src.domain.create_node_usecase import CreateNodeUseCase
from src.domain.reschedule_node_usecase import RescheduleNodeUseCase
from src.interfaces.interface import Interface
from src.event_bus import EventBus
from src.core.scheduling_engine import SchedulingEngine
from src.repositories import NodeRepository
from src.services.cache.pending_review_cache import PendingReviewCache
from src.services.cleanup_service import CleanupService
from src.services.node_format_service import NodeFormatService
from src.services.priority_service import PriorityService
from src.sources.registry import SourceRegistry
from src.services.node_service import NodeService
from src.services.fsrs_service import FsrsService
from src.services.collection_service import CollectionService
from src.services.review_service import ReviewService
from src.services.ressource_service import RessourceService
from src.services.node_orchestrator import NodeOrchestrator
from src.services.fragment_service import FragmentService
from src.services.spore_service import SporeService
from src.services.review_orchestrator import ReviewOrchestrator
from src.services.user_service import UserService
from src.services.node_view_builder import NodeViewBuilder
import logging

logger = logging.getLogger(__name__)


class Application():
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()
        setup_logging(self.config.get("log_level"))
        self.bus = EventBus()
        self.db = Db(Path(self.config["db_path"]))
        self.app_infos = AppInfos()

        print(f"Running Mycel {self.app_infos.version}")

        source_registry = SourceRegistry(self.config["network_user_agent"])
        html_to_markdown_registry = HtmlToMdRegistry()

        node_repository = NodeRepository(self.db)
        lexical_order = LexicalOrder()
        
        ressource_service = RessourceService(source_registry, html_to_markdown_registry)
        node_format_service = NodeFormatService()
        priority_service = PriorityService(node_repository, lexical_order)
        node_service = NodeService(node_repository)

        user_service = UserService(self.db)

        scheduling_engine = SchedulingEngine(user_service)

        create_node_usecase = CreateNodeUseCase(node_service, priority_service)
        create_fragment_usecase = CreateFragmentUseCase(node_service, scheduling_engine, create_node_usecase)

        fragment_service = FragmentService(node_service, node_format_service, create_fragment_usecase)
        spore_service = SporeService(node_service, node_format_service, create_node_usecase)

        collection_service = CollectionService(self.db)
        fsrs_service = FsrsService(collection_service, node_service)

        node_view_builder = NodeViewBuilder(node_service, priority_service)

        pending_review_cache = PendingReviewCache()
        review_service = ReviewService(self.db, scheduling_engine, fsrs_service, node_service, pending_review_cache)

        create_node_from_url_usecase = CreateNodeFromUrlUseCase(create_fragment_usecase, ressource_service)

        reschedule_node_usecase = RescheduleNodeUseCase(node_service, pending_review_cache)

        node_orchestrator = NodeOrchestrator(node_service, fragment_service, spore_service, priority_service, ressource_service, node_view_builder, node_format_service, create_node_from_url_usecase, reschedule_node_usecase)
        
        review_orchestrator = ReviewOrchestrator(user_service, node_service, review_service, node_view_builder)

        self.cleanup_service = CleanupService(node_service, collection_service, user_service)
        
        services = {
            "user_service": user_service,
            "node_service": node_service,
            "collection_service": collection_service,
            "review_service": review_service,
            "ressource_service": ressource_service,
            "fragment_service": fragment_service,
            "spore_service": spore_service,
            "priority_service": priority_service,
        }

        orchestrators = {
            "node_orchestrator": node_orchestrator,
            "review_orchestrator": review_orchestrator
        }

        self.interface = Interface(config = self.config, bus = self.bus, app_infos = self.app_infos, services = services, orchestrators = orchestrators)
        
    # self.bus.subscribe("say_hello", self.say_hello)

    # async def say_hello(self, data=None):
    #     print(data)

    async def init_async(self):
        asyncio.create_task(self.scheduled_loop(self.cleanup_service))
        await self.interface.init_interface()

    async def scheduled_loop(self, cleanup_sevice: CleanupService):
        await cleanup_sevice.clean_deleted_nodes()
        while True:
            await asyncio.sleep(3600)
            try:
                await cleanup_sevice.clean_deleted_nodes()
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")

    def load_config(self):
        with open(self.config_file, "r") as f:
            self.config = json.load(f)
        return self.config
    
    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

def setup_logging(level_str):
    LOG_LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    level = LOG_LEVELS.get(level_str, logging.INFO)
    logging.basicConfig(
        level=level,  
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

if __name__ == "__main__":
    app = Application()
    asyncio.run(app.init_async())
    
