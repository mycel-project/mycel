import asyncio
import json

from src.db import Db
from src.interfaces.interface import Interface
from src.event_bus import EventBus
from src.parsers.parser_registry import ParserRegistry
from src.services import NodeService, FsrsService, CollectionService, ReviewService, ParsingService, RessourceService

class Application():
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()

        self.bus = EventBus()
        self.db = Db()
        self.parser_registry = ParserRegistry()

        ressource_service = RessourceService(self.config["network_user_agent"])
        parsing_service = ParsingService(self.parser_registry)
        node_service = NodeService(self.db, parsing_service, ressource_service)
        collection_service = CollectionService(self.db)
        fsrs_service = FsrsService(collection_service, node_service)
        review_service = ReviewService(self.db, fsrs_service, node_service)

        services = {
            "node_service": node_service,
            "collection_service": collection_service,
            "review_service": review_service
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
        
if __name__ == "__main__":
    app = Application()
    asyncio.run(app.init_async())
    
