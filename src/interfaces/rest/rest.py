from typing import Optional, Union, Any, Annotated
from scalar_fastapi import get_scalar_api_reference

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
from src.models.user import User
from src.models.user_conf import UserConf
from src.schemas.node_detail_view import NodeDetailView
from src.schemas.node_view import NodeView
from src.schemas.user_update import UserUpdate
from src.schemas.collection_update import CollectionUpdate
from src.schemas.collection_view import CollectionView
from src.schemas.config_update import ConfigUpdate
from src.schemas.node_update import NodeUpdate
from src.schemas.user_view import UserView
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
from src.services.user_orchestrator import UserOrchestrator
from src.services.user_service import UserService
from src.types.node_type import NodeType
from src.utils.env import is_testing

from typing import Generic, TypeVar
T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    data: T

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
        self.user_orchestrator: UserOrchestrator = orchestrators["user_orchestrator"]
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

        @self.app.get("/schemas/user-settings", tags=["system"])
        async def get_user_settings_schema() -> ApiResponse[dict]:
            """
            Returns the user settings schema dynamically.
            Implementations can render a fully dynamic settings UI by parsing field types and metadata
            (category, unit, step, warning, etc.) without hardcoding any specific field names or values.
            """ 
            return ApiResponse(data=UserConf.model_json_schema())
        
        # USERS

        class UserCreateRequest(BaseModel):
            name: str
        @self.app.post("/users", tags=["users"])
        async def create_user(data: UserCreateRequest) -> ApiResponse[UserView]:
            user = self.user_orchestrator.create_user(data.name)
            return ApiResponse(data=user)

        @self.app.get("/users/{user_id}", tags=["users"])
        async def get_user(user_id: int, _ = Depends(self.get_user)) -> ApiResponse[UserView]:
            return ApiResponse(data=self.user_orchestrator.get_user(user_id))

        @self.app.patch("/users/{user_id}", tags=["users"])
        async def update_user(user_id: int, data: UserUpdate, _ = Depends(self.get_user)) -> ApiResponse[UserView]:
            user = self.user_orchestrator.update_user(user_id, data)
            return ApiResponse(data=user)

        # COLLECTIONS

        @self.app.get("/collections", tags=["collections"])
        async def list_collections(user_id = Depends(self.get_user)) -> ApiResponse[list[CollectionView]]:
            collections = self.collection_orchestrator.get_collections(user_id)
            return ApiResponse(data=collections)

        class CollectionCreateRequest(BaseModel):
            name: str
        @self.app.post("/collections", tags=["collections"])
        async def create_collection(data: CollectionCreateRequest, user_id = Depends(self.get_user)) -> ApiResponse[CollectionView]:
            collection = self.collection_orchestrator.create_collection(data.name, user_id)
            return ApiResponse(data=collection)

        @self.app.delete("/collections/{col_id}", status_code = 204, tags=["collections"])
        async def delete_collection(col_id: int, user_id = Depends(self.get_user)):
            self.collection_service.delete_collection(col_id)

        @self.app.patch("/collections/{col_id}", tags=["collections"])
        async def update_collection(col_id: int, data: CollectionUpdate, user_id = Depends(self.get_user)):
            collection = self.collection_orchestrator.update_collection(col_id, data)
            return ApiResponse(data=collection)

        # NODES
        
        @self.app.get("/collections/{col_id}/nodes", tags=["nodes"])
        async def list_nodes(col_id: int, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeView]]:
            nodes = self.node_orchestrator.get_nodes_view(col_id, 10000)
            return ApiResponse(data=nodes)

        @self.app.post("/collections/{col_id}/nodes", tags=["nodes"])
        async def create_node(col_id: int, data: NodeCreate, tz_offset: int = 0, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            node = self.node_orchestrator.create_node_to_detail_view(col_id, data, tz_offset)
            return ApiResponse(data=node)
        
        @self.app.get("/collections/{col_id}/nodes/priorities", tags=["nodes"])
        async def get_priorities(col_id: int, user_id = Depends(self.get_user)) -> ApiResponse[dict[int, float]]:
            """
            Priority is a relative value, so adding or modifying a node invalidates other priorities. This route allows the frontend to refresh all priorities in a collection efficiently.
            """
            return ApiResponse(data=self.node_orchestrator.get_priorities(col_id))

        @self.app.get("/collections/{col_id}/nodes/deleted", tags=["nodes"])
        async def get_deleted_nodes(col_id: int, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeView]]:
            """
            Returns all soft-deleted nodes in a collection.
            """
            return ApiResponse(data=self.node_orchestrator.get_deleted_nodes_view(col_id))
        
        @self.app.get("/collections/{col_id}/nodes/{node_id}", tags=["nodes"])
        async def get_node(col_id: int, node_id: int, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            node = self.node_orchestrator.get_node_detail_view(node_id)
            return ApiResponse(data=node)

        @self.app.delete("/collections/{col_id}/nodes/{node_id}", tags=["nodes"])
        async def delete_node(col_id: int, node_id: int, user_id = Depends(self.get_user)):
            """Deletes the node and its entire subtree."""
            deleted_ids = self.node_service.soft_delete_subtree(node_id)
            return ApiResponse(data={"deleted_ids": deleted_ids})

        @self.app.patch("/collections/{col_id}/nodes/{node_id}", tags=["nodes"])
        async def update_node(col_id: int, node_id: int, data: NodeUpdate, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            updated_node = self.node_orchestrator.update_node_to_detail_view(node_id, data)
            return ApiResponse(data=updated_node)
        
        @self.app.get("/collections/{col_id}/nodes/{node_id}/root", tags=["nodes"])
        async def get_root_node(col_id: int, node_id: int, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Get the highest parent node for the given node_id.
            Useful when the frontend is not using a cache and the node tree is deeply nested,
            allows reaching the root without traversing multiple calls manually.
            """
            return ApiResponse(data=self.node_orchestrator.get_root_node(node_id))
    
        class RescheduleNodeRequest(BaseModel):
            date: str       # "2026-05-20"
            tz_offset: int  # minutes
        @self.app.post("/collections/{col_id}/nodes/{node_id}/reschedule", tags=["nodes"])
        async def reschedule_node(col_id: int, node_id: int, data: RescheduleNodeRequest, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Reschedule a node to a specific date.
            """
            return ApiResponse(data=self.node_orchestrator.reschedule_node_to_detail_view(col_id, node_id, data.date, data.tz_offset))

        class RestoreNodeRequest(BaseModel):
            restore_ancestors: bool = False
            restore_descendants: bool = False
        @self.app.post("/collections/{col_id}/nodes/{node_id}/restore", tags=["nodes"])
        async def restore_nodes(col_id: int, node_id: int, body: RestoreNodeRequest, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeView]]:
            """Restore a node, optionally including its parents and/or children."""
            return ApiResponse(data=self.node_orchestrator.restore_nodes_to_views(
                node_id,
                restore_ancestors=body.restore_ancestors,
                restore_descendants=body.restore_descendants,
            ))




        
        @self.app.get("/collections/{col_id}/nodes/{node_id}/outline")
        async def get_outline_node(col_id: int, node_id: int, user_id = Depends(self.get_user)):
            outline = self.node_orchestrator.get_outline_for_node(col_id, node_id)
            return {"outline": outline}

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


        class ReprioritiseNode(BaseModel):
            priority: float 
        @self.app.post("/collections/{col_id}/nodes/{node_id}/reprioritise")
        async def reprioritise_node(col_id: int, node_id: int, data: ReprioritiseNode, user_id = Depends(self.get_user)):
            node = self.node_orchestrator.reprioritise_node_to_view(
                col_id,
                node_id,
                data.priority)
            return {"node": node}

        class SelectionData(BaseModel):
            text: str
            field: int
            start_index: int
            end_index: int
        @self.app.post("/collections/{col_id}/nodes/{node_id}/remove-links")
        async def remove_links(col_id: int, node_id: int, data: SelectionData, user_id = Depends(self.get_user)):
            node = self.node_orchestrator.remove_links_to_view(col_id, node_id, data.text, data.field, data.start_index, data.end_index)
            return {"node": node}

        @self.app.post("/collections/{col_id}/nodes/{node_id}/split")
        async def split_node(col_id: int, node_id: int, level: int, tz_offset: int = 0, user_id = Depends(self.get_user)):
            nodes = self.node_orchestrator.split_node_to_views(col_id, node_id, tz_offset, level)
            return {"nodes": nodes}




        
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

        @self.app.get("/scalar", include_in_schema=False)
        async def scalar_html():
            return get_scalar_api_reference(openapi_url="/openapi.json", title="Mon API")
