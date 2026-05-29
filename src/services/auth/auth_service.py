from abc import ABC, abstractmethod

from fastapi import Request

from src.models.user import User

class AuthService(ABC):
    @abstractmethod
    async def get_authenticated_users(self, request: Request) -> list[User]:
        pass
