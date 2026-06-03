import json
import time
from typing import Optional
from uuid import uuid4
from src.models.user import User
from src.models.user_conf import UserConf

class UserRepository:
    def __init__(self, db):
        self.db = db

    def _row_to_model(self, row) -> User:
        return User(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            conf=UserConf.model_validate(
                json.loads(row["conf"]) if isinstance(row["conf"], str) else row["conf"]
            ),
        )

    def create(self, name: str, conf: UserConf, id: Optional[str] = None) -> User:
        now = int(time.time() * 1000)
        if id is None:
            id = str(uuid4())
        self.db.execute(
            "INSERT INTO users (id, name, created_at, conf) VALUES (:id, :name, :created_at, :conf)",
            {"id": id, "name": name, "created_at": now, "conf": json.dumps(conf.model_dump())},
        )
        return User(id=id, name=name, created_at=now, conf=conf)

    def get(self, id: str) -> Optional[User]:
        row = self.db.fetch_one("SELECT * FROM users WHERE id = :id", {"id": id})
        return self._row_to_model(row) if row else None

    def update(self, user: User) -> None:
        self.db.execute(
            "UPDATE users SET name = :name, conf = :conf WHERE id = :id",
            {"name": user.name, "conf": user.conf.model_dump_json(), "id": user.id},
        )

    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM users WHERE id = :id", {"id": id})

    def list(self) -> list[User]:
        rows = self.db.fetch_all("SELECT * FROM users ORDER BY created_at")
        return [self._row_to_model(r) for r in rows]
