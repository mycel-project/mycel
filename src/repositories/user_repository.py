import json
import time
from typing import Optional
from uuid import uuid4
from src.db import Db
from src.models.user import User
from src.models.user_conf import UserConf

class UserRepository:
    def __init__(self, db: Db):
        self.db = db

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
        return User.from_db(row) if row else None

    def update(self, user: User) -> None:
        self.db.execute(
            "UPDATE users SET name = :name, conf = :conf WHERE id = :id",
            {"name": user.name, "conf": user.conf.model_dump_json(), "id": user.id},
        )

    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM users WHERE id = :id", {"id": id})

    def list(self) -> list[User]:
        rows = self.db.fetch_all("SELECT * FROM users ORDER BY created_at")
        return [User.from_db(r) for r in rows]

    def get_pending_node_id(self, user_id: str) -> str | None:
        row = self.db.fetch_one("SELECT pending_node_id FROM users WHERE id = :id", {"id": user_id})
        return row["pending_node_id"] if row else None

    def set_pending_node_id(self, user_id: str, node_id: str | None) -> None:
        self.db.execute(
            "UPDATE users SET pending_node_id = :node_id WHERE id = :id",
            {"node_id": node_id, "id": user_id},
        )
