from typing import Optional

from src.db import DEFAULT_USER_ID, Db
from src.domain.domain_exceptions import NoUserFound
from src.models.user import User
from src.models.user_conf import UserConf
from src.schemas.user_update import UserUpdate
from src.repositories.user_repository import UserRepository
from src.schemas.user_view import UserView
from src.services.node_service import deep_update_dict


class UserService:
    def __init__(self, db: Db, ensure_default_user: bool):
        self._repo = UserRepository(db)
        if ensure_default_user:
            try:
                self.get_user(DEFAULT_USER_ID)
            except NoUserFound:
                self.create_user("default", DEFAULT_USER_ID)

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
        id: Optional[str] = None,
    ) -> User:
        return self._repo.create(
            name=name,
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
            templates=user.templates,
        )

    def to_views(self, users: list[User]) -> list[UserView]:
        return [self.to_view(c) for c in users]

    def update(self, user_id: str, updates: UserUpdate) -> User:
        user = self.get_user(user_id)

        changes = updates.model_dump(exclude_unset=True)
        merged_data = deep_update_dict(user.model_dump(), changes)
        updated_user = User.model_validate(merged_data)

        self._repo.update(updated_user)
        return updated_user

    def get_pending_review(self, user_id: str) -> str | None:
        return self._repo.get_pending_review_id(user_id)

    def set_pending_review(self, user_id: str, node_id: str) -> None:
        self._repo.set_pending_review_id(user_id, node_id)

    def clear_pending_review(self, user_id: str) -> None:
        self._repo.set_pending_review_id(user_id, None)
