import uvicorn
import asyncio
import socket

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
        local_ip = self.get_local_ip()
        print(f"Network: {local_ip}:{self.port}")
        await self.server.serve()
        self.active = False
        self.server = None
        self.task = None
        
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    async def start(self, app):
        if not self.active:
            self.task = asyncio.create_task(self._serve(app))
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def stop(self):
        if self.server is not None and self.active:
            print("Stopping Uvicorn...")
            self.server.should_exit = True
            if self.task:
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
