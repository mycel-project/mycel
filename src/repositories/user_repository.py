from typing import Optional
from src.db import Db
from src.models.user import User

class UserRepository:
    def __init__(self, db: Db):
        self.db = db

    def create(self, name: str, id: Optional[str] = None) -> User:
        if id is not None:
            user = User(name=name, id=id)
        else:
            user = User(name=name)

        self.db.execute(
            "INSERT INTO users (id, name, created_at, conf, templates) VALUES (:id, :name, :created_at, :conf, :templates)",
            {
                "id": user.id,
                "name": user.name,
                "created_at": user.created_at,
                "conf": user.conf.model_dump_json(),
                "templates": user.templates.model_dump_json(),
            },
        )
        return user

    def get(self, id: str) -> Optional[User]:
        row = self.db.fetch_one("SELECT * FROM users WHERE id = :id", {"id": id})
        return User.model_validate(row) if row else None

    def update(self, user: User) -> None:
        self.db.execute(
            "UPDATE users SET name = :name, conf = :conf, templates = :templates WHERE id = :id",
            {"name": user.name, "conf": user.conf.model_dump_json(), "templates": user.templates.model_dump_json(), "id": user.id},
        )

    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM users WHERE id = :id", {"id": id})

    def list(self) -> list[User]:
        rows = self.db.fetch_all("SELECT * FROM users ORDER BY created_at")
        return [User.model_validate(r) for r in rows]

    def get_pending_node_id(self, user_id: str) -> str | None:
        row = self.db.fetch_one("SELECT pending_node_id FROM users WHERE id = :id", {"id": user_id})
        return row["pending_node_id"] if row else None

    def set_pending_node_id(self, user_id: str, node_id: str | None) -> None:
        self.db.execute(
            "UPDATE users SET pending_node_id = :node_id WHERE id = :id",
            {"node_id": node_id, "id": user_id},
        )
