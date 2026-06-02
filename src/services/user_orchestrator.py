from src.schemas.user_update import UserUpdate
from src.schemas.user_view import UserView
from src.services.user_service import UserService


class UserOrchestrator:
    def __init__(
        self,
        user_service: UserService,
    ):
        self._user_service = user_service

    def create_user(self, name: str = "Mycel") -> UserView:
        user = self._user_service.create_user(name=name)
        return self._user_service.to_view(user)

    def get_user(self, user_id: int) -> UserView:
        user = self._user_service.get_user(user_id=user_id)
        return self._user_service.to_view(user)

    def update_user(self, user_id: int, updates: UserUpdate) -> UserView:
        user = self._user_service.update(user_id=user_id, updates=updates)
        return self._user_service.to_view(user)
