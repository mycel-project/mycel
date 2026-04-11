import click
import sys

from src.interfaces.base_interface import BaseInterface
from .commands import create_cli_group


class Cli(BaseInterface):
    def __init__(self):
        self.cli_group = None
    
    async def init(self, config, bus, services):
        self.config = config
        self.bus = bus
        self.node_service = services["node_service"]
        self.collection_service = services["collection_service"]
        self.review_service = services["review_service"]
        self.ressource_service = services["ressource_service"]

        self.cli_group = create_cli_group(
            node_service=self.node_service,
            collection_service=self.collection_service,
            review_service=self.review_service,
            ressource_service=self.ressource_service,
            bus=self.bus
        )
        
        await self.start()

    async def start(self):
        if self.cli_group is None:
            raise RuntimeError("CLI not initialized.")

        self.cli_group.main(args=sys.argv[1:], standalone_mode=True)

