import time

from src.repositories.idempotency_repository import IdempotencyRepository


class IdempotencyService:
    EXPIRY_MS = 60 * 60 * 1000  

    def __init__(self, repo: IdempotencyRepository):
        self._repo = repo

    def get(self, user_id: str, key: str) -> dict | None:
        return self._repo.get(user_id, key)

    def set(self, user_id: str, key: str, response_body: dict) -> None:
        self._repo.set(user_id, key, response_body)
        self._repo.purge_expired(int(time.time() * 1000) - self.EXPIRY_MS)
