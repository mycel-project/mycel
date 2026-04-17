import asyncio
import json

from pathlib import Path

from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.db import Db
from src.interfaces.interface import Interface
from src.event_bus import EventBus
from src.core.scheduling_engine import SchedulingEngine
from src.sources.registry import SourceRegistry
from src.services import NodeService, FsrsService, CollectionService, ReviewService, RessourceService
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
        node_service = NodeService(self.db, ressource_service)
        collection_service = CollectionService(self.db)
        fsrs_service = FsrsService(collection_service, node_service)
        scheduling_engine = SchedulingEngine()
        review_service = ReviewService(self.db, scheduling_engine, fsrs_service, node_service)

        services = {
            "node_service": node_service,
            "collection_service": collection_service,
            "review_service": review_service,
            "ressource_service": ressource_service
        }

        self.interface = Interface(config = self.config, bus = self.bus, services = services)
        
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
        level=logging.WARNING,  
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

if __name__ == "__main__":
    setup_logging()
    app = Application()
    asyncio.run(app.init_async())
    
