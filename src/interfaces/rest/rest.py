from typing import Optional, Union, Any, Annotated
import logging
from pydantic import Field

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.core.app_infos import AppInfos
from src.core.config import MycelConfig, DeploymentMode
from src.core.regex import CLOZE_REGEX
from src.domain.domain_exceptions import DomainException, Unauthorized
from src.event_bus import EventBus
from src.interfaces.base_interface import BaseInterface
from src.interfaces.uvicorn import UvicornServer
from src.models.node_create import NodeCreate
from src.models.collection import Collection
from src.models.type_review_data import TypeReviewData
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData
from src.models.user_conf_update import UserConfUpdate
from src.schemas.collection_view import CollectionView
from src.schemas.config_update import ConfigUpdate
from src.schemas.node_update import NodeUpdate
from src.services.auth.auth_service import AuthService
from src.services.collection_orchestrator import CollectionOrchestrator
from src.services.collection_service import CollectionService
from src.services.fragment_service import FragmentService
from src.services.node_orchestrator import NodeOrchestrator
from src.services.node_service import NodeService
from src.services.priority_service import PriorityService
from src.services.review_orchestrator import ReviewOrchestrator
from src.services.review_service import ReviewService
from src.services.spore_service import SporeService
from src.services.user_service import UserService
from src.types.node_type import NodeType
from src.utils.env import is_testing

logger = logging.getLogger(__name__)

class Rest(BaseInterface):
    def __init__(self, app_infos):
        self.app_infos: AppInfos = app_infos
        self.app = FastAPI(
            title="Mycel API",
            version=self.app_infos.version,
        )
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._register_routes()

    async def init(self, config: MycelConfig, bus, services, orchestrators):
        # Would be better if interfaces only had access to orchestrators?
        self.config = config
        self.bus: EventBus = bus
        self.user_service: UserService = services["user_service"]
        self.node_service: NodeService = services["node_service"]
        self.collection_service: CollectionService = services["collection_service"]
        self.review_service: ReviewService = services["review_service"]
        self.priority_service: PriorityService = services["priority_service"]
        self.collection_orchestrator: CollectionOrchestrator = orchestrators["collection_orchestrator"]
        self.node_orchestrator: NodeOrchestrator = orchestrators["node_orchestrator"]
        self.review_orchestrator: ReviewOrchestrator = orchestrators["review_orchestrator"]
        self.auth_service: AuthService | None = services["auth_service"]
        self.uvicorn = UvicornServer()
        if not is_testing():
            await self.start()
        
    async def start(self):
        await self.uvicorn.start(self.app)

    async def stop(self):
        if self.uvicorn.active:
            await self.uvicorn.stop()

    async def get_user(self, request: Request) -> str:
        if self.config.deployment_mode == DeploymentMode.CLOUD:
            assert self.auth_service != None
            return await self.auth_service.get_user_id(request.headers.get("Authorization", "")) # For now MycelCloud is single user.
        else:
            return "1" # Defaut User for self-hosting

    def _register_routes(self):
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            logger.error(str(exc.errors()))
            return JSONResponse(
                status_code=422,
                content={
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request",
                    "errors": exc.errors(),
                },
            )

        @self.app.exception_handler(DomainException)
        async def domain_exception_handler(request: Request, exc: DomainException):
            logger.error(exc.message)
            logger.error(exc.code)
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "code": exc.code,
                    "message": exc.message,
                },
            )


        # SYSTEM
        
        @self.app.get("/health", tags=["system"])
        async def check_reachability():
            """
            Checks that Mycel is reachable and running.
            """
            return {"status": "ok"}

        class VersionResponse(BaseModel):
            version: str
        @self.app.get("/version", tags=["system"])
        async def version() -> VersionResponse:
            """
            Get the current Mycel version.
            """
            return VersionResponse(version=self.app_infos.version)

        class ClozeRegex(BaseModel):
            regex: str
        @self.app.get("/constants/cloze-regex", tags=["system"])
        async def get_cloze_regex() -> ClozeRegex:
            """
            Get cloze regex used to manipulate cloze field of spores.
            """
            return ClozeRegex(regex=CLOZE_REGEX)
        
        @self.app.get("/users/settings/schema")
        async def user_config_schema():
            schema = self.user_service.get_user_config_schema()
            return {"schema": schema}        

        # COLLECTIONS
        
        @self.app.get("/collections", tags=["collections"])
        async def list_collections(user_id = Depends(self.get_user)):
            collections = self.collection_service.get_collections(user_id)
            return {"collections": collections}

        @self.app.get("/collections/{col_id}", tags=["collections"])
        async def get_collection_details(col_id: int, user_id = Depends(self.get_user)):
            data = self.collection_service.get_collection_details(col_id)
            return {"collection_details": data}

        class CollectionCreate(BaseModel):
            name: str
        @self.app.post("/collections", tags=["collections"])
        async def create_collection(data: CollectionCreate, user_id = Depends(self.get_user)):
            collection = self.collection_service.create_collection(data.name, user_id)
            return {"collection": CollectionListView.model_validate(collection)}

        @self.app.delete("/collections/{collection_id}", status_code = 204, tags=["collections"])
        async def delete_collection(collection_id: int, user_id = Depends(self.get_user)):
            self.collection_service.delete_collection(collection_id)

        class CollectionUpdate(BaseModel):
            newName: str | None = None
            config: ConfigUpdate | None = None # We could be more precise here with a schema
        @self.app.patch("/collections/{col_id}", tags=["collections"])
        async def update_collections(col_id: int,  data: CollectionUpdate, user_id = Depends(self.get_user)):
            if data.newName is not None:
                self.collection_service.rename_collection(col_id, data.newName)
            if data.config is not None:
                self.collection_service.update_configs(col_id, data.config)
            return {"status": "ok"}

        @self.app.get("/collections/{col_id}/nodes", tags=["collections"])
        async def get_nodes(col_id: int, user_id = Depends(self.get_user)):
            nodes = self.node_orchestrator.get_nodes_view(col_id, 10000)
            return {"nodes": nodes}

        @self.app.get("/collections/{col_id}/nodes/priorities")
        async def get_priorities(col_id: int, user_id = Depends(self.get_user)):
            # This route is important because adding or modifying a node's priority on the frontend invalidates other priorities, as priority is a relative value. It allows quickly refreshing all node priorities in a collection.
            priorities = self.node_orchestrator.get_priorities(col_id)
            return {"priorities": priorities}

        @self.app.get("/collections/{col_id}/nodes/deleted")
        async def get_deleted_nodes(col_id: int, user_id = Depends(self.get_user)):
            nodes = self.node_service.get_deleted_nodes_view(col_id)
            return {"nodes": nodes}

        @self.app.get("/collections/{col_id}/nodes/{node_id}")
        async def get_node(col_id: int, node_id: int, user_id = Depends(self.get_user)):
            node = self.node_orchestrator.get_node_view(node_id)
            return {"node": node}

        @self.app.get("/collections/{col_id}/nodes/{node_id}/root")
        async def get_root_node(col_id: int, node_id: int, user_id = Depends(self.get_user)):
            """
            For convenience
            Get the highest parent node for the given node_id.
            Useful when the frontend is not using a cache and the node tree is deeply nested.
            Allows quickly reaching the root without having to traverse manually through multiple calls.
            """
            node = self.node_orchestrator.get_root_node(node_id)
            return {"node": node}
        
        @self.app.post("/collections/{col_id}/nodes/{node_id}/split")
        async def split_node(col_id: int, node_id: int, level: int, tz_offset: int = 0, user_id = Depends(self.get_user)):
            nodes = self.node_orchestrator.split_node_to_views(col_id, node_id, tz_offset, level)
            return {"nodes": nodes}

        @self.app.get("/collections/{col_id}/nodes/{node_id}/outline")
        async def get_outline_node(col_id: int, node_id: int, user_id = Depends(self.get_user)):
            outline = self.node_orchestrator.get_outline_for_node(col_id, node_id)
            return {"outline": outline}
 
        @self.app.get("/collections/{col_id}/nodes/{node_id}")
        async def get_node_metrics(col_id: int, node_id: int, user_id = Depends(self.get_user)):
            return self.node_service.get_node_metrics(node_id)

        @self.app.delete("/collections/{col_id}/nodes/{node_id}")
        async def delete_node(col_id: int, node_id: int, user_id = Depends(self.get_user)):
            """Deletes the node and its entire subtree."""
            deleted_ids = self.node_service.soft_delete_subtree(node_id)
            return {"deleted_ids": deleted_ids}

        
        class RescheduleNodeRequest(BaseModel):
            date: str       # "2026-05-20"
            tz_offset: int  # minutes
        @self.app.post("/collections/{col_id}/nodes/{node_id}/reschedule")
        async def reschedule_node(col_id: int, node_id: int, data: RescheduleNodeRequest, user_id = Depends(self.get_user)):
            node = self.node_orchestrator.reschedule_node_to_view(col_id, node_id, data.date, data.tz_offset)
            return {"node": node}

        class RestoreNodeRequest(BaseModel):
            restore_ancestors: bool = False
            restore_descendants: bool = False
        @self.app.post("/collections/{col_id}/nodes/{node_id}/restore")
        async def restore_nodes(col_id: int, node_id: int, body: RestoreNodeRequest, user_id = Depends(self.get_user)):
            """Restore a node, optionally including its parents and/or children."""
            nodes = self.node_orchestrator.restore_nodes_to_views(
                node_id,
                restore_ancestors=body.restore_ancestors,
                restore_descendants=body.restore_descendants,
            )
            return {"nodes": nodes}
            
        class NodeExtract(BaseModel):
            text: str
            field: int
            start_index: int
            end_index: int
            extract_type: NodeType
            tz_offset: int = 0
        @self.app.post("/collections/{col_id}/nodes/{node_id}/extracts")
        async def create_node_extract(col_id: int, node_id: int, data: NodeExtract, user_id = Depends(self.get_user)):
            extract_result = self.node_orchestrator.create_extract(col_id, data.extract_type, node_id, data.text, data.field, data.start_index, data.end_index, data.tz_offset)
            return extract_result.model_dump()
            
        @self.app.post("/collections/{col_id}/nodes")
        async def create_node(col_id: int, data: NodeCreate, tz_offset: int = 0, user_id = Depends(self.get_user)):
            node = self.node_orchestrator.create_node_to_view(col_id, data, tz_offset) 
            return {"node": node}

        class ReprioritiseNode(BaseModel):
            priority: float 
        @self.app.post("/collections/{col_id}/nodes/{node_id}/reprioritise")
        async def reprioritise_node(col_id: int, node_id: int, data: ReprioritiseNode, user_id = Depends(self.get_user)):
            node = self.node_orchestrator.reprioritise_node_to_view(
                col_id,
                node_id,
                data.priority)
            return {"node": node}

        @self.app.patch("/collections/{col_id}/nodes/{node_id}")
        async def update_node(col_id: int, node_id: int, data: NodeUpdate, user_id = Depends(self.get_user)):
            updated_node = self.node_orchestrator.update_node_to_view(
                node_id,
                data
            )
            return {"node": updated_node}

        class SelectionData(BaseModel):
            text: str
            field: int
            start_index: int
            end_index: int
        @self.app.post("/collections/{col_id}/nodes/{node_id}/remove-links")
        async def remove_links(col_id: int, node_id: int, data: SelectionData, user_id = Depends(self.get_user)):
            node = self.node_orchestrator.remove_links_to_view(col_id, node_id, data.text, data.field, data.start_index, data.end_index)
            return {"node": node}

        
        # @self.app.post("/collections/{col_id}/reindex")
        # async def reindex(col_id: int):
        #     self.node_service.reindex_all(col_id)
        #     return {"status": "ok"}

        class ReviewData(BaseModel):
            duration: int # generic data for all reviews no matter the node type
            type_review_data: TypeReviewData # data specific to node type
            tz_offset: int = 0
        @self.app.post("/collections/{col_id}/nodes/{node_id}/spore-review")
        async def review_spore(col_id: int, node_id: int, data: ReviewData, user_id = Depends(self.get_user)):
            node = self.review_orchestrator.review_to_view(col_id, node_id, data.duration, data.type_review_data, tz_offset_min=data.tz_offset)
            return {"node": node}

        @self.app.post("/collections/{col_id}/nodes/{node_id}/fragment-review")
        async def review_fragment(col_id: int, node_id: int, data: ReviewData, user_id = Depends(self.get_user)):
            node = self.review_orchestrator.review_to_view(col_id, node_id, data.duration, data.type_review_data, tz_offset_min=data.tz_offset)
            return {"node": node}

        @self.app.get("/collections/{col_id}/reviews/calendar")
        async def get_calendar(col_id: int, tz_offset: int = 0, user_id = Depends(self.get_user)):
            # Goal : ?start=2025-01-01&end=2025-05-31&include=reviewed,due
            calendar = self.review_orchestrator.get_calendar(
                col_id,
                tz_offset_minutes=tz_offset,
                done = False
            )
            return {"calendar": calendar}

        @self.app.post("/collections/{col_id}/reviews/undo")
        async def undo_review(col_id: int, user_id = Depends(self.get_user)):
            node_from_undone_review = self.review_orchestrator.undo_review(col_id)
            return {"node": node_from_undone_review}

        @self.app.get("/collections/{col_id}/reviews/next")
        async def get_next_review(col_id: int, tz_offset: int = 0, user_id = Depends(self.get_user)):
            node = self.review_orchestrator.get_next_review(col_id, tz_offset)
            return {"node": node}

        @self.app.get("/users", tags=["users"])
        async def list_users(request: Request, user_id = Depends(self.get_user)):               
            return {"users": users}
        
        @self.app.get("/users/me")
        async def get_current_user(user_id = Depends(self.get_user)):
            return {"user": user_id}

        @self.app.patch("/users/me/settings")
        async def update_user_conf(data: UserConfUpdate, user_id = Depends(self.get_user)):
            user = self.user_service.update_user_conf(user_id, data)
            return {"user": user}
