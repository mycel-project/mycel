from typing import Optional, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.interfaces.base_interface import BaseInterface
from src.interfaces.uvicorn import UvicornServer
from src.schemas import node_metrics

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
        self.node_service = services["node_service"]
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

        @self.app.get("/collections/{col_id}/nodes")
        async def get_nodes(col_id: int):
            nodes = self.node_service.get_nodes(col_id, 10)
            return {"nodes": nodes}

        @self.app.get("/collections/{col_id}/nodes/{node_id}")
        async def get_node_metrics(col_id: int, node_id: int):
            return self.node_service.get_node_metrics(node_id)

        class NodeCreate(BaseModel):
            content: Union[str, dict]
        @self.app.post("/collections/{col_id}/nodes")
        async def create_node(col_id: int, data: NodeCreate):
            self.node_service.create_node(col_id, data.content)

        class ReprioritiseNode(BaseModel):
            new_position_node_id: int
        @self.app.post("/collections/{col_id}/nodes/{node_id}/reprioritise")
        async def reprioritise_node(col_id: int, node_id: int, data: ReprioritiseNode):
            self.node_service.reprioritise_node(
                node_id,
                data.new_position_node_id
            )
            return {"status": "ok"}

        class NodeUpdate(BaseModel):
            content: Optional[Union[str, dict]] = None
            metrics: Optional[Union[str, dict]] = None
            type: Optional[int] = None
        @self.app.patch("/collections/{col_id}/nodes/{node_id}")
        async def update_node(col_id: int, node_id: int, data: NodeUpdate):
            self.node_service.update(node_id, data.dict(exclude_unset=True))
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
            self.node_service.reindex(col_id)
            return {"status": "ok"}

        class CollectionConfigsUpdate(BaseModel):
            configModel: str
            updates: dict
        @self.app.patch("/collections/{col_id}")
        async def update_collections_configs(col_id: int,  data: CollectionConfigsUpdate):
            self.collection_service.update_configs(col_id, data.configModel, data.updates)
            return {"status": "ok"}

