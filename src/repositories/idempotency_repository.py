import json
import time

from src.db import Db

class IdempotencyRepository:
    def __init__(self, db: Db):
        self.db = db
        
    def get(self, user_id: str, key: str) -> dict | None:
        row = self.db.fetch_one(
            "SELECT response_body FROM idempotency_keys WHERE user_id = :user_id AND id = :key",
            {"user_id": user_id, "key": key}
        )
        return json.loads(row["response_body"]) if row else None

    def set(self, user_id: str, key: str, response_body: dict) -> None:
        self.db.execute(
            "INSERT INTO idempotency_keys (id, user_id, response_body, created_at) VALUES (:key, :user_id, :body, :now)",
            {"key": key, "user_id": user_id, "body": json.dumps(response_body), "now": int(time.time() * 1000)}
        )

    def purge_expired(self, cutoff_ms: int) -> None:
        self.db.execute(
            "DELETE FROM idempotency_keys WHERE created_at < :cutoff",
            {"cutoff": cutoff_ms}
        )
