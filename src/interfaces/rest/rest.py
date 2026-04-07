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
        self.collection_service = services["collection_service"]
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

        @self.app.get("/collections/{col_id}/cards")
        async def get_cards(col_id: int):
            cards = self.card_service.get_cards(col_id, 10)
            return {"cards": cards}

        class CardCreate(BaseModel):
            front: str
            back: str
        @self.app.post("/collections/{col_id}/cards")
        async def create_card(col_id: int, data: CardCreate):
            self.card_service.create_card(col_id, data.model_dump())

        class ReprioritiseCard(BaseModel):
            new_position_card_id: int
        @self.app.post("/collections/{col_id}/cards/{card_id}/reprioritise")
        async def reprioritise_card(col_id: int, card_id: int, data: ReprioritiseCard):
            self.card_service.reprioritise_card(
                card_id,
                data.new_position_card_id
            )
            return {"status": "ok"}

        @self.app.get("/collections")
        async def get_collections():
            collections = self.collection_service.get_collections()
            return {"collections": collections}

        @self.app.get("/collections/{colId}")
        async def get_collection_details(colId: int):
            data = self.collection_service.get_collection_detailed(colId)
            return {"details": data}

        class CollectionCreate(BaseModel):
            name: str
        @self.app.post("/collections")
        async def create_collection(data: CollectionCreate):
            self.collection_service.create_collection(data.name)
            return {"status": "ok"}

        class CollectionRename(BaseModel):
            newName: str
        @self.app.post("/collections/{colId}/rename")
        async def rename_collection(colId: int, data: CollectionRename):
            self.collection_service.rename_collection(colId, data.newName)
            return {"status": "ok"}
            
        @self.app.post("/collections/{col_id}/reindex")
        async def reindex(col_id: int):
            self.card_service.reindex(col_id)
            return {"status": "ok"}

        class CollectionConfigsUpdate(BaseModel):
            configModel: str
            updates: dict
        @self.app.patch("/collections/{col_id}")
        async def update_collections_configs(col_id: int,  data: CollectionConfigsUpdate):
            self.collection_service.update_configs(col_id, data.configModel, data.updates)
            return {"status": "ok"}

