import uvicorn
import asyncio

class UvicornServer:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.task = None
        self.active = False

    async def _serve(self, app):
        config = uvicorn.Config(app, host=self.host, port=self.port, log_level="info", )
        self.server = uvicorn.Server(config)
        self.active = True
        await self.server.serve()
        self.active = False
        self.server = None
        self.task = None

    async def start(self, app):
        if not self.active:
            self.task = asyncio.create_task(self._serve(app))

    async def stop(self):
        if self.server is not None and self.active:
            print("Stopping Uvicorn...")
            self.server.should_exit = True
            if self.task:
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
