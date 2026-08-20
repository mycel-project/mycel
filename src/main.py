import asyncio
import json
import sys
from io import TextIOWrapper

from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.core.app_infos import AppInfos
from src.core.config import MycelConfig, load_config
from src.core.lexical_order import LexicalOrder
from src.db import Db
from src.domain.create_fragment_usecase import CreateFragmentUseCase
from src.domain.create_node_from_text_usecase import CreateNodeFromTextUseCase
from src.domain.create_node_from_url_usecase import CreateNodeFromUrlUseCase
from src.domain.create_node_usecase import CreateNodeUseCase
from src.domain.create_spore_usecase import CreateSporeUseCase
from src.domain.get_outline_usecase import GetOutlineUseCase
from src.domain.reprioritise_usecase import ReprioritiseUseCase
from src.domain.reschedule_usecase import RescheduleUseCase
from src.domain.split_node_usecase import SplitNodeUseCase
from src.interfaces.interface import Interface
from src.event_bus import EventBus
from src.core.scheduling_engine import SchedulingEngine
from src.repositories import NodeRepository, CollectionRepository, LearningUnitRepository
from src.repositories.idempotency_repository import IdempotencyRepository
from src.services.auth.auth_service import AuthService
from src.services.cleanup_service import CleanupService
from src.services.collection_orchestrator import CollectionOrchestrator
from src.services.idempotency_service import IdempotencyService
from src.services.import_export_service import ImportExportService
from src.services.node_format_service import NodeFormatService
from src.services.priority_service import PriorityService
from src.services.user_orchestrator import UserOrchestrator
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
if isinstance(sys.stdout, TextIOWrapper):
    sys.stdout.reconfigure(line_buffering=True)

class Application():
    def __init__(self, auth_service: AuthService | None = None, db_path: str | None = None):
        self.config_file = "config.json"
        self.config = load_config(self.config_file)
        setup_logging(self.config.log_level)
        self.bus = EventBus()
        if db_path: # to overwrite path during tests. Use custom db_path or the one provided in config
            from src.core.config import build_db_url
            self.db = Db(build_db_url(db_path))
        else:
            self.db = Db(self.config.sqlalchemy_url)
        self.app_infos = AppInfos()

        if self.config.run_migrations_on_startup and not self.db.testing:
            from alembic import command
            from alembic.config import Config
            from alembic.script import ScriptDirectory
            from sqlalchemy.exc import OperationalError

            logger.info("Running database migrations...")
            alembic_cfg = Config("alembic.ini")

            try:
                command.upgrade(alembic_cfg, "head")
            except OperationalError as e:
                if "already exists" in str(e):
                    logger.warning(
                        "Existing schema detected with no Alembic history. "
                        "Stamping database as baseline and retrying migrations."
                    )
                    script = ScriptDirectory.from_config(alembic_cfg)
                    base_revision = script.get_base()
                    if base_revision is None:
                        raise RuntimeError("No Alembic migrations found in alembic/versions/")
                    command.stamp(alembic_cfg, base_revision)
                    command.upgrade(alembic_cfg, "head")
                else:
                    raise
                
        print(f"Running Mycel {self.app_infos.version}")

        source_registry = SourceRegistry(self.config.network_user_agent, self.config.allow_private_urls_fetch)
        html_to_markdown_registry = HtmlToMdRegistry()

        node_repository = NodeRepository(self.db)
        learning_unit_repository = LearningUnitRepository(self.db)
        lexical_order = LexicalOrder()
        
        ressource_service = RessourceService(source_registry, html_to_markdown_registry)
        node_format_service = NodeFormatService()
        priority_service = PriorityService(learning_unit_repository, lexical_order)
        node_service = NodeService(node_repository, learning_unit_repository)

        collection_repository = CollectionRepository(self.db)
        
        collection_service = CollectionService(collection_repository)
        
        user_service = UserService(self.db)
        user_orchestrator = UserOrchestrator(user_service, collection_service, self.config.ensure_default_user)

        scheduling_engine = SchedulingEngine(user_service)

        self.create_node_usecase = CreateNodeUseCase(node_service, priority_service)
        self.create_fragment_usecase = CreateFragmentUseCase(node_service, scheduling_engine, self.create_node_usecase)
        self.create_spore_usecase = CreateSporeUseCase(node_service, scheduling_engine, self.create_node_usecase)

        fragment_service = FragmentService(node_service, node_format_service, self.create_fragment_usecase)
        spore_service = SporeService(user_service, node_service, node_format_service, self.create_spore_usecase)

        fsrs_service = FsrsService(collection_service, node_service)

        node_view_builder = NodeViewBuilder(node_service, priority_service)

        review_service = ReviewService(self.db, scheduling_engine, fsrs_service, node_service)

        create_node_from_url_usecase = CreateNodeFromUrlUseCase(self.create_fragment_usecase, ressource_service)
        create_node_from_text_usecase = CreateNodeFromTextUseCase(self.create_fragment_usecase)

        reschedule_usecase = RescheduleUseCase(user_service, node_service)
        reprioritise_usecase = ReprioritiseUseCase(node_service, priority_service)

        get_outline_usecase = GetOutlineUseCase()
        split_node_usecase = SplitNodeUseCase(node_service, self.create_fragment_usecase, get_outline_usecase)

        collection_orchestrator = CollectionOrchestrator(collection_service)
        
        node_orchestrator = NodeOrchestrator(node_service, fragment_service, spore_service, priority_service, ressource_service, node_view_builder, node_format_service, create_node_from_url_usecase, create_node_from_text_usecase, reschedule_usecase, reprioritise_usecase, get_outline_usecase, split_node_usecase, collection_service)

        review_orchestrator = ReviewOrchestrator(user_service, node_service, review_service, node_view_builder, collection_service)

        idempotency_repository = IdempotencyRepository(self.db)
        idempotency_service = IdempotencyService(idempotency_repository)

        ie_service = ImportExportService(self.db, self.app_infos)

        self.cleanup_service = CleanupService(node_service, collection_service, user_service)
        
        self.services = {
            "user_service": user_service,
            "node_service": node_service,
            "collection_service": collection_service,
            "review_service": review_service,
            "ressource_service": ressource_service,
            "fragment_service": fragment_service,
            "spore_service": spore_service,
            "priority_service": priority_service,
            "auth_service": auth_service,
            "idempotency_service": idempotency_service,
            "ie_service": ie_service,
        }

        self.orchestrators = {
            "user_orchestrator": user_orchestrator,
            "collection_orchestrator": collection_orchestrator,
            "node_orchestrator": node_orchestrator,
            "review_orchestrator": review_orchestrator,
        }

        self.interface = Interface(config = self.config, bus = self.bus, app_infos = self.app_infos, services = self.services, orchestrators = self.orchestrators)
        
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
    
