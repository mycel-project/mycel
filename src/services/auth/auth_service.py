from abc import ABC, abstractmethod

class AuthService(ABC):
    @abstractmethod
    async def get_user_id(self, authorization: str) -> str:
        pass
