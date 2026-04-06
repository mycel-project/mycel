from .uvicorn import UvicornServer
from .websocket import Ws
from src.interfaces.base_interface import BaseInterface


class Web(BaseInterface):
    def __init__(self, host="0.0.0.0", port=8000):
        pass
    
    async def init(self, config, bus):
        self.config = config
        self.bus = bus
        self.uvicorn = UvicornServer()
        self.ws = Ws(bus)
        await self.start()

    async def start(self):
        await self.uvicorn.start()

    async def stop(self):
        if self.uvicorn.active:
            await self.uvicorn.stop()
