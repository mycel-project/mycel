import asyncio

from src.db import Db
from pybase import Application_bones, Menu
from src.interfaces.interface import Interface
from src.event_bus import EventBus
from src.services import NodeService, review_node, CollectionService

class Application(Application_bones):
    def __init__(self):
        name = "plm"
        config = "config.json"
        modules = {
            "menu": {
                "class": Menu,
            },
            "db": {
                "class": Db,
            },
            "interface": {
                "class": Interface,
            },
        }
        menu = {
            "main": {
                1:{
                    "name":"web",
                    "description":"Placeholder",
                    "action": lambda: self.menu.get_menu("main")
                },
                "parent": None
            }
        }
        super().__init__(name, config, menu, modules)
        self.bus = EventBus()
        self.init_module("db")
        
        node_service = NodeService(self.db)
        collection_service = CollectionService(self.db)

        services = {
            "node_service": node_service,
            "collection_service": collection_service
        }
        self.init_module("interface", config = self.config, bus = self.bus, services = services)

    # self.bus.subscribe("say_hello", self.say_hello)

    # async def say_hello(self, data=None):
    #     print(data)

    async def init_async(self):
        await self.interface.init_interface()

if __name__ == "__main__":
    app = Application()
    asyncio.run(app.run())
    
    # from src.repositories.node_repository import NodeRepository
    # from src.repositories.collection_repository import CollectionRepository
    # db = Db()

    # # Collections
    # col_repo = CollectionRepository(db)
    # col = col_repo.create("Ma collection")
    # col = col_repo.get(col.id)

    # # Cartes
    # node_repo = NodeRepository(db)
    # node = node_repo.create(col.id, data={"front": "...", "back": "..."}, tags=["python"])
    # node = node_repo.get(node.id)
    
