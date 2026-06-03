from typing import Optional

from pydantic import ValidationError
from src.db import Db
from src.domain.domain_exceptions import NoUserFound
from src.models.user import User
from src.models.user_conf import UserConf
from src.schemas.user_conf_update import UserConfUpdate
from src.schemas.user_update import UserUpdate
from src.repositories.user_repository import UserRepository
from src.schemas.user_view import UserView


class UserService:
    def __init__(self, db: Db):
        self._repo = UserRepository(db)

    def get_user(self, user_id: str) -> User:
        user = self._repo.get(user_id)
        if user is None:
            raise NoUserFound(user_id)
        return user

    def get_users(self) -> list[User]:
        # Add logic to select multiple users and juste show them ? or in orhestrator ?
        return self._repo.list()
    
    def create_user(
        self,
        name: str,
        user_conf: Optional[UserConf] = None,
        id: Optional[str] = None,
    ) -> User:
        if user_conf is None:
            user_conf = UserConf()
        return self._repo.create(
            name=name,
            conf=user_conf,
            id=id,
        )

    def get_config(
        self,
        user_id: str
    ) -> UserConf:
        user = self.get_user(user_id)
        return user.conf

    def get_undo_max_age_min(
        self,
        user_id: str
    ) -> int:
        minutes = self.get_config(user_id).undo_review_max_age
        return minutes

    def get_wait_for_due_time(
        self,
        user_id: str
    ) -> int:
        return self.get_config(user_id).wait_for_due_time

    def delete_user(self, user_id: str) -> None:
        self.get_user(user_id)
        self._repo.delete(user_id)

    def to_view(self, user: User) -> UserView:
        return UserView(
            id=user.id,
            name=user.name,
            conf=user.conf,
            created_at=user.created_at,
        )

    def to_views(self, users: list[User]) -> list[UserView]:
        return [self.to_view(c) for c in users]

    def update(self, user_id: str, updates: UserUpdate) -> User:
        user = self.get_user(user_id)

        for field in updates.model_fields_set: 
            value = getattr(updates, field)
            setattr(user, field, value)
            
        self._repo.update(user)
        return user
