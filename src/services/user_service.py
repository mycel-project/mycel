from typing import Optional

from pydantic import ValidationError
from src.db import Db
from src.domain.domain_exceptions import NoUserFound
from src.models.user import User
from src.models.user_conf import UserConf
from src.models.user_conf_update import UserConfUpdate
from src.models.user_update import UserUpdate
from src.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Db):
        self._repo = UserRepository(db)

    def get_user(self, user_id: int) -> User:
        user = self._repo.get(user_id)
        if user is None:
            raise NoUserFound(user_id)
        return user

    def get_users(self) -> list[User]:
        return self._repo.list()
    
    def create_user(
        self,
        name: str,
        user_conf: Optional[UserConf] = None
    ) -> User:
        if user_conf is None:
            user_conf = UserConf()
        return self._repo.create(
            name=name,
            conf=user_conf
        )

    def delete_user(self, user_id: int) -> None:
        self.get_user(user_id)
        self._repo.delete(user_id)

    def update_user_conf(self, user_id: int, conf_update: UserConfUpdate) -> User:
        user = self.get_user(user_id)
        updated_data = user.conf.model_dump()
        for field, value in conf_update:
            if value is not None:
                updated_data[field] = value
        user.conf = UserConf(**updated_data)
        self._repo.update(user)
        return user
    
    def rename_user(self, user_id: int, new_name: str) -> User:
        return self.update_user(
            user_id,
            UserUpdate(
                name=new_name
            )
        )

    def update_user(self, user_id: int, updates: UserUpdate) -> User:
        user = self.get_user(user_id)
        for field, value in updates:
            if value is not None:
                setattr(user, field, value)
        self._repo.update(user)
        return user

    def get_user_config_schema(self):
        return UserConf.model_json_schema()
        
