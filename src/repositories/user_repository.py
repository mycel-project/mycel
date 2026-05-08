import json
import time
from typing import Optional

from src.models.user import User
from src.models.user_conf import UserConf
from src.models.user_update import UserUpdate


class UserRepository:
    def __init__(self, db):
        self.db = db

    def _row_to_model(self, row) -> User:
        return User(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            conf=UserConf.model_validate(
                json.loads(row["conf"])
                if isinstance(row["conf"], str)
                else row["conf"]
            ),
        )
 
    def create(
        self,
        name: str,
        conf: UserConf,
    ) -> User:
        now = int(time.time() * 1000)

        self.db.execute(
            """
            INSERT INTO users (id, name, created_at, conf)
            VALUES (?, ?, ?, ?)
            """,
            (
                now,
                name,
                now,
                json.dumps(conf.model_dump()),
            ),
        )
        return User(
            id=now,
            name=name,
            created_at=now,
            conf=conf,
        )

    def get(self, id: int) -> Optional[User]:
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (id,),
        )
        return self._row_to_model(row) if row else None

    def update(self, user: User) -> None:
        self.db.execute(
            "UPDATE users SET name = ?, conf = ? WHERE id = ?",
            (user.name, user.conf.model_dump_json(), user.id),
        )

    def delete(self, id: int) -> None:
        self.db.execute(
            "DELETE FROM users WHERE id = ?",
            (id,),
        )

    def list(self) -> list[User]:
        rows = self.db.fetch_all(
            "SELECT * FROM users ORDER BY created_at"
        )
        return [self._row_to_model(r) for r in rows]
