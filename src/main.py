import asyncio

from src.db import Db
from pybase import Application_bones, Menu

class Application(Application_bones):
    def __init__(self):
        name = "plm"
        config = "config.json"
        modules = {
            "menu": {
                "class": Menu,
                "app": True,
            },
            "db": {
                "class": Db,
            }
        }
        menu = {
            "main": {
                1:{
                    "name":"web",
                    "description":"Launch web socket interface",
                    "action":lambda: self.web.start()
                },
                "parent": None
            }
        }
        super().__init__(name, config, menu, modules)
        self.init_module("db")

if __name__ == "__main__":
    app = Application()
    asyncio.run(app.run())
    
