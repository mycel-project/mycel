from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.interfaces.base_interface import BaseInterface
from src.interfaces.uvicorn import UvicornServer

class Rest(BaseInterface):
    def __init__(self):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._register_routes()

    async def init(self, config, bus, services):
        self.config = config
        self.bus = bus
        self.card_service = services["card_service"]
        self.uvicorn = UvicornServer()
        await self.start()
        
    async def start(self):
        await self.uvicorn.start(self.app)

    async def stop(self):
        if self.uvicorn.active:
            await self.uvicorn.stop()
        
    def _register_routes(self):
        @self.app.get("/")
        async def root():
            return {"message": "Hello World"}

        @self.app.get("/cards")
        async def get_cards(collection_id: int):
            cards = self.card_service.get_cards(collection_id, 10)
            return {"cards": cards}

        class CardCreate(BaseModel):
            front: str
            back: str
        @self.app.post("/cards/create")
        async def create_card(data: CardCreate):
            collection_id = 1775496678952
            self.card_service.create_card(collection_id, data.model_dump())

        class ReprioritiseCard(BaseModel):
            new_position_card_id: int
        @self.app.post("/cards/{card_id}/reprioritise")
        async def reprioritise_card(card_id: int, data: ReprioritiseCard):
            self.card_service.reprioritise_card(
                card_id,
                data.new_position_card_id
            )
            return {"status": "ok"}

        @self.app.post("/collections/{collection_id}/reindex")
        async def reindex(collection_id):
            collection_id = 1775496678952
            self.card_service.reindex(collection_id)
            return {"status": "ok"}
