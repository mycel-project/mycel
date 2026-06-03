import os
import time
from typing import Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .schema import Base
from .models import *
from dotenv import load_dotenv

load_dotenv()

class Db:
    def __init__(self, db_path: str, testing: bool = False):
        self.testing = testing
        db_path = os.getenv("DATABASE_URL") or db_path
        self.db_path = db_path
        if str(db_path).startswith("postgresql"):
            url = str(db_path)
        else:
            url = f"sqlite:///{db_path}"
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

        with self.session_factory() as session:
            existing = session.execute(text("SELECT id FROM users WHERE id = :id"), {"id": 1}).fetchone()
            if not existing:
                session.execute(text("INSERT INTO users (id, name, created_at, conf) VALUES (:id, :name, :now, '{}')"), {"id": 1, "name": "default", "now": int(time.time() * 1000)})
                session.commit()

    @property
    def is_sqlite(self) -> bool:
        """
        The codebase is otherwise fully agnostic to the database dialect.
        This property exists solely to handle SQLite-specific SQL syntax where needed (e.g. json_extract vs ::jsonb).
        """
        return "sqlite" in str(self.engine.url)

    def execute(self, query: str, params: tuple | dict = ()) -> None:
        with self.session_factory() as session:
            session.execute(text(query), self._to_dict(params))
            session.commit()

    def fetch_one(self, query: str, params: tuple | dict = ()) -> Any:
        with self.session_factory() as session:
            return session.execute(text(query), self._to_dict(params)).mappings().fetchone()

    def fetch_all(self, query: str, params: tuple | dict = ()) -> list[Any]:
        with self.session_factory() as session:
            return list(session.execute(text(query), self._to_dict(params)).mappings().fetchall())

    def clear_all(self):
        if not self.testing:
            raise PermissionError("Safety check failed: clear_all can only be run on test databases.")
        with self.session_factory() as session:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
            
    def _to_dict(self, params: tuple | dict) -> dict:
        if isinstance(params, dict):
            return params
        return {f"param{i}": v for i, v in enumerate(params)}
