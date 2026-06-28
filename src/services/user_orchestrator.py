from src.db import DEFAULT_USER_ID
from src.domain.domain_exceptions import NoUserFound
from src.schemas.user_update import UserUpdate
from src.schemas.user_view import UserView
from src.services.collection_service import CollectionService
from src.services.user_service import UserService


class UserOrchestrator:
    def __init__(
        self,
        user_service: UserService,
        collection_service: CollectionService,
        ensure_default_user: bool = False,
    ):
        self._user_service = user_service
        self._collection_service = collection_service

        if ensure_default_user:
            try:
                self._user_service.get_user(DEFAULT_USER_ID)
            except NoUserFound:
                self.create_user("default", DEFAULT_USER_ID)

    def create_user(self, name: str = "Mycel", user_id = None) -> UserView:
        user = self._user_service.create_user(name=name, id=user_id)
        self._collection_service.create_collection("Default", user.id)
        return self._user_service.to_view(user)
    
    def get_user(self, user_id: str) -> UserView:
        user = self._user_service.get_user(user_id=user_id)
        return self._user_service.to_view(user)

    def update_user(self, user_id: str, updates: UserUpdate) -> UserView:
        user = self._user_service.update(user_id=user_id, updates=updates)
        return self._user_service.to_view(user)
