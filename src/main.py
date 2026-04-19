import asyncio
import json

from pathlib import Path

from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.db import Db
from src.interfaces.interface import Interface
from src.event_bus import EventBus
from src.core.scheduling_engine import SchedulingEngine
from src.services.node_format_service import NodeFormatService
from src.sources.registry import SourceRegistry
from src.services import NodeService, FsrsService, CollectionService, ReviewService, RessourceService, NodeOrchestrator, FragmentService, SporeService
import logging

class Application():
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()
        self.bus = EventBus()
        self.db = Db(Path(self.config["db_path"]))

        source_registry = SourceRegistry(self.config["network_user_agent"])
        html_to_markdown_registry = HtmlToMdRegistry()

        ressource_service = RessourceService(source_registry, html_to_markdown_registry)
        node_format_service = NodeFormatService()
        node_service = NodeService(self.db, ressource_service)
        fragment_service = FragmentService(node_service, node_format_service)
        spore_service = SporeService(node_service, node_format_service)

        collection_service = CollectionService(self.db)
        fsrs_service = FsrsService(collection_service, node_service)
        scheduling_engine = SchedulingEngine()
        review_service = ReviewService(self.db, scheduling_engine, fsrs_service, node_service)

        node_orchestrator = NodeOrchestrator(node_service, fragment_service, spore_service)

        services = {
            "node_service": node_service,
            "collection_service": collection_service,
            "review_service": review_service,
            "ressource_service": ressource_service,
            "fragment_service": fragment_service,
            "spore_service": spore_service,
        }

        orchestrators = {
            "node_orchestrator": node_orchestrator,
        }

        self.interface = Interface(config = self.config, bus = self.bus, services = services, orchestrators = orchestrators)
        
    # self.bus.subscribe("say_hello", self.say_hello)

    # async def say_hello(self, data=None):
    #     print(data)


    async def init_async(self):
        await self.interface.init_interface()

    def load_config(self):
        with open(self.config_file, "r") as f:
            self.config = json.load(f)
        return self.config
    
    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

if __name__ == "__main__":
    setup_logging()
    app = Application()
    asyncio.run(app.init_async())
    
