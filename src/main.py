import asyncio

from src.db import Db
from pybase import Application_bones, Menu
from src.interfaces.interface import Interface
from src.event_bus import EventBus

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
        self.bus.subscribe("say_hello", self.say_hello)
        self.init_module("db")
        self.init_module("interface", config = self.config, bus = self.bus)

    async def say_hello(self, data=None):
        print(data)

    async def init_async(self):
        await self.interface.init_interface()

if __name__ == "__main__":
    app = Application()
    asyncio.run(app.run())
    
