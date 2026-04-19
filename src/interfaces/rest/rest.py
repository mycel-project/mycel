from typing import Optional, Union, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.event_bus import EventBus
from src.interfaces.base_interface import BaseInterface
from src.interfaces.uvicorn import UvicornServer
from src.schemas.node_update import NodeUpdate
from src.services.collection_service import CollectionService
from src.services.fragment_service import FragmentService
from src.services.node_orchestrator import NodeOrchestrator
from src.services.node_service import NodeService
from src.services.review_service import ReviewService
from src.services.spore_service import SporeService
from src.types.node_type import NodeType


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

    async def init(self, config, bus, services, orchestrators):
        # Would be better if interfaces only had access to orchestrators?
        self.config = config
        self.bus: EventBus = bus
        self.node_service: NodeService = services["node_service"]
        self.collection_service: CollectionService = services["collection_service"]
        self.review_service: ReviewService = services["review_service"]
        self.node_orchestrator: NodeOrchestrator = orchestrators["node_orchestrator"]
        self.uvicorn = UvicornServer()
        await self.start()
        
    async def start(self):
        await self.uvicorn.start(self.app)

    async def stop(self):
        if self.uvicorn.active:
            await self.uvicorn.stop()

    def _register_routes(self):
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            print("VALIDATION ERROR:", exc.errors())
            return JSONResponse(
                status_code=422,
                content={"detail": exc.errors()},
            )
        
        @self.app.get("/")
        async def root():
            return {"message": "Hello World"}

        @self.app.get("/node-types")
        async def get_node_types():
            return {
                "types": [
                    {"label": t.name, "value": t.value}
                    for t in NodeType
                ]
            }

        @self.app.get("/collections/{col_id}/nodes")
        async def get_nodes(col_id: int):
            nodes = self.node_service.get_nodes(col_id, 100)
            return {"nodes": nodes}

        @self.app.get("/collections/{col_id}/nodes/{node_id}")
        async def get_node_metrics(col_id: int, node_id: int):
            return self.node_service.get_node_metrics(node_id)

        class NodeCreate(BaseModel):
            content: Union[str, dict]
            type: int
        @self.app.post("/collections/{col_id}/nodes")
        async def create_node(col_id: int, data: NodeCreate):
            self.node_orchestrator.create_node_dispatch(col_id, data.type, data.content)
            
        class NodeExtract(BaseModel):
            text: str
            field: int
            start_index: int
            end_index: int
            type: NodeType
        @self.app.post("/collections/{col_id}/nodes/{node_id}/extracts")
        async def create_node_extract(col_id: int, node_id: int, data: NodeExtract):
            self.node_orchestrator.create_extract(col_id, data.type, node_id, data.text, data.field, data.start_index, data.end_index)

        class NodeCreateFromUrl(BaseModel):
            url: str
        @self.app.post("/collections/{col_id}/nodes/from-url")
        async def create_node_from_url(col_id: int, data: NodeCreateFromUrl):
            self.node_service.create_node_from_url(col_id, data.url)
            return {"status": "ok"}

        class ReprioritiseNode(BaseModel):
            new_position_node_id: int
        @self.app.post("/collections/{col_id}/nodes/{node_id}/reprioritise")
        async def reprioritise_node(col_id: int, node_id: int, data: ReprioritiseNode):
            self.node_service.reprioritise_node(
                node_id,
                data.new_position_node_id
            )
            return {"status": "ok"}

        class NodeUpdateRequest(BaseModel):
            updates: dict[str, Any] = Field(default_factory=dict)
        @self.app.patch("/collections/{col_id}/nodes/{node_id}")
        async def update_node(col_id: int, node_id: int, data: NodeUpdateRequest):
            self.node_service.update(node_id, NodeUpdate(**data.updates))
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

        class NodeReview(BaseModel):
            rating: int
            duration: int
        @self.app.post("/collections/{col_id}/nodes/{node_id}/reviews")
        async def review_node(col_id: int, node_id: int, data: NodeReview):
            self.review_service.review(col_id, node_id, data.rating, data.duration)
            return {"status": "ok"}
