from typing import Optional, cast
import json
from scalar_fastapi import get_scalar_api_reference

import logging
import asyncio

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from src.core.app_infos import AppInfos
from src.core.config import MycelConfig
from src.core.regex import CLOZE_REGEX
from src.core.version import check_version_compatibility
from src.core.version_exception import VersionException
from src.domain.domain_exceptions import DomainException, NoUserFound
from src.interfaces.base_interface import BaseInterface
from src.interfaces.uvicorn import UvicornServer
from src.models.day_review_overview import DayReviewOverview
from src.models.dto.node_slot_priority import NodeSlotPriority
from src.models.dto.review_target import ReviewTarget
from src.models.export import FullExport
from src.models.extract_result import ExtractResult
from src.models.node import NodeType
from src.models.node_create import NodeCreate
from src.models.node_slot_key import NodeSlotKey
from src.models.outline import Outline
from src.models.type_review_data import TypeReviewData
from src.models.user_conf import UserConf
from src.schemas.learning_unit_update import LearningUnitUpdate
from src.schemas.node_detail_view import NodeDetailView
from src.schemas.node_view import NodeView
from src.schemas.user_update import UserUpdate
from src.schemas.collection_update import CollectionUpdate
from src.schemas.collection_view import CollectionView
from src.schemas.node_update import NodeUpdate
from src.schemas.user_view import UserView
from src.services.auth.auth_service import AuthService
from src.services.collection_orchestrator import CollectionOrchestrator
from src.services.idempotency_service import IdempotencyService
from src.services.import_export_service import ImportExportService
from src.services.node_orchestrator import NodeOrchestrator
from src.services.review_orchestrator import ReviewOrchestrator
from src.services.user_orchestrator import UserOrchestrator
from src.utils.env import is_testing

from typing import Generic, TypeVar

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    data: T

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

AUTH_RESPONSES = {
    401: {"description": "Unauthorized - see Mycel implementation guide."},
    402: {"description": "Unsubscribed - see Mycel implementation guide."},
    503: {"description": "Service unavailable - see Mycel implementation guide."},
}

tags_metadata = [
            {
                "name": "system",
            },
            {
                "name": "users",
            },
            {
                "name": "collections",
            },
            {
                "name": "nodes",
                "description": """Endpoints relative to nodes. To act on learning unit-specific data, see the dedicated section. Node endpoints here only affect global node attributes, even when the node has a single learning unit (as is the case with fragments)."""
            },
            {
                "name": "learning units",
                "description": """Endpoints relative to a learning unit within a node, targeted using its slot number. Returns the fully updated node.

For common actions (such as reprioritisation), you can use dedicated endpoints. For more advanced control and precise updates, you should use the Update Learning Unit endpoint.

Endpoint names reflect the target learning unit type when the action is type-specific (e.g. dismiss_fragment rather than dismiss_learning_unit).

*If you don't want to support mutliple-learning-unit nodes, always pass 1 as the slot number.*
                """
            },
            {
                "name": "reviews",
            },
        ]

class Rest(BaseInterface):
    def __init__(self, app_infos):
        self.app_infos: AppInfos = app_infos
        self.app = FastAPI(
            title="Mycel API",
            version=self.app_infos.version,
            openapi_tags=tags_metadata,  
            description="""
## Version compatibility

All requests may include the `X-Mycel-Version` header to indicate the minimum version your implementation requires (e.g. `2.3.0`). If provided, Mycel will verify compatibility and return a `version` error if incompatible.

See the implementation guide for details.
        """
        )
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._register_routes()

    async def init(self, config: MycelConfig, bus, services, orchestrators):
        self.config = config
        self.idempotency_service: IdempotencyService = services["idempotency_service"]
        self.ie_service: ImportExportService = services["ie_service"]
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

    async def get_user(self, request: Request, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> str:
        if is_testing():
            token = request.headers.get("Authorization", "").split(" ")[1]
            return cast(str, jwt.decode(token, "test_key", algorithms=["HS256"], audience="authenticated").get("sub"))
        if self.auth_service is not None:
            user_id = await self.auth_service.get_user_id(request.headers.get("Authorization", ""))
            try:
                self.user_orchestrator.get_user(user_id)
            except NoUserFound:
                name = await self.auth_service.get_user_name(user_id)
                self.user_orchestrator.create_user(name, user_id)
            return user_id
        from src.db import DEFAULT_USER_ID
        return DEFAULT_USER_ID

    def _register_routes(self):
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            logger.error(str(exc.errors()))
            return JSONResponse(
                status_code=422,
                content={
                    "detail": {
                        "type": "internal",
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid request",
                        "errors": exc.errors(),
                    }
                },
            )

        @self.app.exception_handler(DomainException)
        async def domain_exception_handler(request: Request, exc: DomainException):
            logger.warning(f"{exc.code}: {exc.message}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": {"type": "domain", "code": exc.code, "message": exc.message}},
            )

        @self.app.exception_handler(404)
        async def not_found_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=404,
                content={"detail": {"type": "domain", "code": "route_not_found", "message": str(exc.detail)}},
            )

        @self.app.exception_handler(405)
        async def method_not_allowed_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=405,
                content={"detail": {"type": "domain", "code": "method_not_allowed", "message": str(exc.detail)}},
            )

        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            if isinstance(exc.detail, dict):
                content = {"detail": {"type": "auth", **exc.detail}}
            else:
                content = {"detail": {"type": "auth", "code": "error", "message": str(exc.detail)}}
            return JSONResponse(status_code=exc.status_code, content=content)

        @self.app.exception_handler(Exception)
        async def unhandled_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": {"type": "internal", "code": "internal_error", "message": "Internal server error"}},
            )

        @self.app.middleware("http")
        async def logging_middleware(request: Request, call_next):
            if request.url.path == "/ping":
                return await call_next(request)
            # if not self.config.log_responses:  
            #     return await call_next(request)

            response = await call_next(request)

            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            logger.debug(
                f"{request.method} {request.url.path} "
                f"→ {response.status_code} "
                f"{body.decode('utf-8')[:1000]}"
            )

            return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
                headers=dict(response.headers)
            )

        @self.app.middleware("http")
        async def idempotency_middleware(request: Request, call_next):
            if request.url.path == "/ping":
                return await call_next(request)
            key = request.headers.get("Idempotency-Key")

            if not key or request.method not in ("POST", "PATCH"):
                return await call_next(request)

            user_id = await self.get_user(request)

            cached = self.idempotency_service.get(user_id, key)
            if cached:
                return JSONResponse(content=cached)

            response = await call_next(request)

            if response.status_code < 300:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                self.idempotency_service.set(user_id, key, json.loads(body))
                return Response(content=body, status_code=response.status_code, media_type=response.media_type)

            return response

        @self.app.middleware("http")
        async def version_check_middleware(request: Request, call_next):
            if request.url.path == "/ping":
                return await call_next(request)
            required_min_version = request.headers.get("X-Mycel-Version")
            if required_min_version:
                try:
                    check_version_compatibility(required_min_version, self.app_infos.version)
                except VersionException as e:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": {"type": "version", "code": e.code, "message": e.message}}
                    )
            return await call_next(request)

        @self.app.get("/scalar", include_in_schema=False)
        async def scalar_html():
            return get_scalar_api_reference(openapi_url="/openapi.json", title="Mon API")

        # SYSTEM

        @self.app.get("/ping", tags=["system"])
        async def check_reachability():
            """
            Checks Mycel liveness. 
            """
            return {"status": "ok"}
        
        @self.app.get("/health", tags=["system"])
        async def check_health(user_id = Depends(self.get_user)):
            """
            Checks that client can use the API: server reachability, version and authentication.
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
            user_id: str | None = None
            name: str 
        @self.app.post("/users", tags=["users"])
        async def create_user(data: UserCreateRequest) -> ApiResponse[UserView]: 
            """
            Note: This route is only accessible in self-hosted deployments. It is blocked at the infrastructure level in MycelCloud, as users are created internally during account registration.
            """
            user = self.user_orchestrator.create_user(data.name, data.user_id)
            return ApiResponse(data=user)

        @self.app.get("/users", tags=["users"], responses={**AUTH_RESPONSES})
        async def get_user(user_id = Depends(self.get_user)) -> ApiResponse[UserView]:
            return ApiResponse(data=self.user_orchestrator.get_user(user_id))

        @self.app.patch("/users", tags=["users"], responses={**AUTH_RESPONSES})
        async def update_user(data: UserUpdate, user_id = Depends(self.get_user)) -> ApiResponse[UserView]:
            user = self.user_orchestrator.update_user(user_id, data)
            return ApiResponse(data=user)

        @self.app.get("/users/export", tags=["users"], responses={**AUTH_RESPONSES})
        async def export_user_data(user_id = Depends(self.get_user)) -> ApiResponse[FullExport]:
            user_data = self.ie_service.export_data(user_id)
            return ApiResponse(data=user_data)

        @self.app.post("/users/import", status_code=204, tags=["users"], responses={**AUTH_RESPONSES})
        async def import_user_data(payload: FullExport, user_id = Depends(self.get_user)):
            self.ie_service.import_data(user_id, payload)

        # COLLECTIONS
        @self.app.get("/collections", tags=["collections"], responses={**AUTH_RESPONSES})
        async def list_collections(user_id = Depends(self.get_user)) -> ApiResponse[list[CollectionView]]:
            collections = self.collection_orchestrator.get_collections(user_id)
            return ApiResponse(data=collections)

        class CollectionCreateRequest(BaseModel):
            name: str
        @self.app.post("/collections", tags=["collections"], responses={**AUTH_RESPONSES})
        async def create_collection(data: CollectionCreateRequest, user_id = Depends(self.get_user)) -> ApiResponse[CollectionView]:
            collection = self.collection_orchestrator.create_collection(data.name, user_id)
            return ApiResponse(data=collection)

        @self.app.delete("/collections/{col_id}", status_code = 204, tags=["collections"], responses={**AUTH_RESPONSES})
        async def delete_collection(col_id: str, user_id = Depends(self.get_user)):
            self.collection_orchestrator.delete_collection(user_id, col_id)

        @self.app.patch("/collections/{col_id}", tags=["collections"], responses={**AUTH_RESPONSES})
        async def update_collection(col_id: str, data: CollectionUpdate, user_id = Depends(self.get_user)) -> ApiResponse[CollectionView]:
            collection = self.collection_orchestrator.update_collection(user_id, col_id, data)
            return ApiResponse(data=collection)

        # NODES
        
        @self.app.get("/collections/{col_id}/nodes", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def list_nodes(col_id: str, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeView]]:
            nodes = self.node_orchestrator.get_nodes_view(user_id, col_id, 10000)
            return ApiResponse(data=nodes)


        @self.app.post("/collections/{col_id}/nodes", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def create_node(col_id: str, data: NodeCreate, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Main endpoint for adding new resources or arbitrary nodes.

            This endpoint handles node creation from a URL or raw text, depending on the "type" discriminator provided. It creates a corresponding Fragment with the metadata provided in the request body.
            """
            node = await asyncio.to_thread(
                self.node_orchestrator.create_node_to_detail_view,
                user_id, col_id, data, data.tz_offset
            )
            return ApiResponse(data=node)
        
        @self.app.get("/collections/{col_id}/nodes/priorities", tags=["learning units"], responses={**AUTH_RESPONSES})
        async def get_priorities(col_id: str, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeSlotPriority]]:
            """
            Priority is a relative value, meaning that adding or modifying a node invalidates other priorities. This route allows the frontend to efficiently refresh all priorities within a collection.
            """
            priorities = self.node_orchestrator.get_priorities(user_id, col_id)
            return ApiResponse(data=[
                NodeSlotPriority(node_id=k.node_id, slot=k.slot, priority=v)
                for k, v in priorities.items()
            ])

        @self.app.get("/collections/{col_id}/nodes/deleted", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def get_deleted_nodes(col_id: str, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeView]]:
            """
            Returns all soft-deleted nodes in a collection.
            """
            return ApiResponse(data=self.node_orchestrator.get_deleted_nodes_view(user_id, col_id))
        
        @self.app.get("/collections/{col_id}/nodes/{node_id}", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def get_node(col_id: str, node_id: str, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            node = self.node_orchestrator.get_node_detail_view(user_id, col_id, node_id)
            return ApiResponse(data=node)
        
        class DeleteNodeResponse(BaseModel):
            deleted_ids: list[str]
        @self.app.delete("/collections/{col_id}/nodes/{node_id}", tags=["nodes"], status_code=200, responses={**AUTH_RESPONSES})
        async def delete_node(col_id: str, node_id: str, user_id = Depends(self.get_user)) -> ApiResponse[DeleteNodeResponse]:
            """
            Soft-deletes the node and its entire subtree. Returns all deleted node ids so the client can update its local state without a full refetch.
            """
            deleted_ids = self.node_orchestrator.soft_delete_subtree(user_id, col_id, node_id)
            return ApiResponse(data=DeleteNodeResponse(deleted_ids=deleted_ids))

        @self.app.patch("/collections/{col_id}/nodes/{node_id}", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def update_node(col_id: str, node_id: str, data: NodeUpdate, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Update Node. To update spore/fragment data, use dedicated endpoints (reprioritise, reschedule, ...) or update_slot endpoint.
            """
            updated_node = self.node_orchestrator.update_node_to_detail_view(user_id, col_id, node_id, data)
            return ApiResponse(data=updated_node)

        @self.app.get("/collections/{col_id}/nodes/{node_id}/root", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def get_root_node(col_id: str, node_id: str, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Get the highest parent node for the given node_id.
            Useful when the frontend is not using a cache and the node tree is deeply nested,
            allows reaching the root without traversing multiple calls manually.
            """
            return ApiResponse(data=self.node_orchestrator.get_root_node(user_id, col_id, node_id))

        @self.app.get("/collections/{col_id}/nodes/{node_id}/outline", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def get_outline(col_id: str, node_id: str, user_id = Depends(self.get_user)) -> ApiResponse[Outline]:
            """
            Returns the outline of the node based on his format. To get an outline for formats unknown to Mycel, use your client's functionality if it can generate one.
            """
            return ApiResponse(data=self.node_orchestrator.get_outline_for_node(user_id, col_id, node_id))

        class RestoreNodeRequest(BaseModel):
            restore_ancestors: bool = False
            restore_descendants: bool = False
        @self.app.post("/collections/{col_id}/nodes/{node_id}/restore", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def restore_nodes(col_id: str, node_id: str, body: RestoreNodeRequest, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeView]]:
            """Restore a node, optionally including its parents and/or children."""
            return ApiResponse(data=self.node_orchestrator.restore_nodes_to_views(
                user_id,
                col_id,
                node_id,
                restore_ancestors=body.restore_ancestors,
                restore_descendants=body.restore_descendants,
            ))
        
        class SelectionData(BaseModel):
            text: str = Field(description="The selected portion.")
            field: str = "content" # Default for fragments
            start_index: int
            end_index: int
        @self.app.post("/collections/{col_id}/nodes/{node_id}/remove-links", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def remove_links(col_id: str, node_id: str, data: SelectionData, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            return ApiResponse(data=self.node_orchestrator.remove_links_to_detail_view(
                user_id, col_id, node_id, data.text, data.field, data.start_index, data.end_index
            ))

        class NodeExtractRequest(SelectionData):
            extract_type: NodeType
            auto_format: bool = Field(default=True, description="Wether to let Mycel emphasis the extracted region based on the Node content_format. Make it False to override Mycel's formatting manually.")
            tz_offset: int = 0
        @self.app.post("/collections/{col_id}/nodes/{node_id}/extracts", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def create_node_extract(col_id: str, node_id: str, data: NodeExtractRequest, user_id = Depends(self.get_user)) -> ApiResponse[ExtractResult]:
            """
            Note: non-idempotent: see Mycel documentation.
            """
            return ApiResponse(data=self.node_orchestrator.create_extract(
                user_id, col_id, data.extract_type, node_id, data.text, data.field, data.start_index, data.end_index, data.auto_format, data.tz_offset
            ))

        class SplitNodeRequest(BaseModel):
            level: int
            field: str = "content"
            auto_format: bool = Field(default=True, description="Wether to let Mycel emphasis the split region based on the Node content_format. Make it False to override Mycel's formatting manually.")
            tz_offset: int = 0
        @self.app.post("/collections/{col_id}/nodes/{node_id}/split", tags=["nodes"], responses={**AUTH_RESPONSES})
        async def split_node(col_id: str, node_id: str, data: SplitNodeRequest, user_id = Depends(self.get_user)) -> ApiResponse[list[NodeDetailView]]:
            """
            Split node by heading level.
            Note: non-idempotent: see Mycel documentation.
            """
            return ApiResponse(data=self.node_orchestrator.split_node_to_detail_views(user_id, col_id, node_id, data.field, data.auto_format, data.tz_offset, data.level))

        ## LEARNING UNITS
        
        @self.app.patch("/collections/{col_id}/nodes/{node_id}/slot/{slot}", tags=["learning units"], responses={**AUTH_RESPONSES})
        async def update_learning_unit(col_id: str, node_id: str, slot: int, data: LearningUnitUpdate, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Updates learning unit data without modifying global Node attributes.
            """
            updated_node = self.node_orchestrator.update_learning_unit_to_detail_view(user_id, col_id, node_id, slot, data)
            return ApiResponse(data=updated_node)
        
        class ReprioritiseRequest(BaseModel):
            priority: float
        @self.app.patch("/collections/{col_id}/nodes/{node_id}/slot/{slot}/reprioritise", tags=["learning units"], responses={**AUTH_RESPONSES})
        async def reprioritise_learning_unit(col_id: str, node_id: str, slot: int, data: ReprioritiseRequest, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Reprioritise a learning unit.
            """
            return ApiResponse(data=self.node_orchestrator.reprioritise_to_detail_view(user_id, col_id, node_id, slot, data.priority))
    
        class RescheduleRequest(BaseModel):
            date: str       # "2026-05-20"
            tz_offset: int  # minutes
        @self.app.patch("/collections/{col_id}/nodes/{node_id}/slot/{slot}/reschedule", tags=["learning units"], responses={**AUTH_RESPONSES})
        async def reschedule_learning_unit(col_id: str, node_id: str, slot: int, data: RescheduleRequest, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Reschedule a learning unit to a specific date.
            """
            return ApiResponse(data=self.node_orchestrator.reschedule_to_detail_view(user_id, col_id, node_id, slot, data.date, data.tz_offset))

        class DismissRequest(BaseModel):
            value: Optional[bool] = None 
        @self.app.patch("/collections/{col_id}/nodes/{node_id}/slot/{slot}/dismiss", tags=["learning units"], responses={**AUTH_RESPONSES})
        async def dismiss_fragment(col_id: str, node_id: str, slot: int, data: DismissRequest = DismissRequest(), user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            """
            Toggle or explicitly set the dismiss state of a fragment.
            If no value is provided, the current state is toggled.
            Only fragments are dismissable.
            """
            return ApiResponse(data=self.node_orchestrator.dismiss_to_detail_view(user_id, col_id, node_id, slot, data.value))

        # REVIEWS

        @self.app.get("/collections/{col_id}/reviews/next", tags=["reviews"], responses={**AUTH_RESPONSES})
        async def get_next_review(col_id: str, tz_offset: int = 0, user_id = Depends(self.get_user)) -> ApiResponse[ReviewTarget | None]:
            return ApiResponse(data=self.review_orchestrator.get_next_review(user_id, col_id, tz_offset))

        @self.app.post("/collections/{col_id}/reviews/undo", tags=["reviews"], responses={**AUTH_RESPONSES})
        async def undo_review(col_id: str, user_id = Depends(self.get_user)) -> ApiResponse[ReviewTarget]:
            """
            Undo the last review. Returns the node from the undone review so the client can navigate back to it.
            Note: non-idempotent: see Mycel documentation.
            """
            return ApiResponse(data=self.review_orchestrator.undo_review(user_id, col_id))

        @self.app.get("/collections/{col_id}/reviews/calendar", tags=["reviews"], responses={**AUTH_RESPONSES})
        async def get_calendar(col_id: str, tz_offset: int = 0, user_id = Depends(self.get_user)) -> ApiResponse[list[DayReviewOverview]]:
            return ApiResponse(data=self.review_orchestrator.get_calendar(
                user_id,
                col_id,
                tz_offset_minutes=tz_offset,
                done=False
            ))

        class ReviewRequest(BaseModel):
            duration: int # generic data for all reviews no matter the node type
            type_review_data: TypeReviewData # data specific to node type
            tz_offset: int = 0
            slot: int = 1
        @self.app.post("/collections/{col_id}/nodes/{node_id}/review", tags=["reviews"], responses={**AUTH_RESPONSES})
        async def review_node(col_id: str, node_id: str, data: ReviewRequest, user_id = Depends(self.get_user)) -> ApiResponse[NodeDetailView]:
            return ApiResponse(data=self.review_orchestrator.review_to_detail_view(user_id, 
                                                                                   col_id, node_id, data.slot, data.duration, data.type_review_data, tz_offset_min=data.tz_offset
            ))
        

        
        # @self.app.post("/collections/{col_id}/reindex")
        # async def reindex(col_id: int):
        #     self.node_service.reindex_all(col_id)
        #     return {"status": "ok"}
