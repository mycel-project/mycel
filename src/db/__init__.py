import time
from pathlib import Path
from typing import Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .schema import Base
from .models import CollectionORM

class Db:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        url = f"sqlite:///{db_path}"
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

        with self.session_factory() as session:
            session.execute(text("""
                INSERT OR IGNORE INTO users (id, name, created_at, conf)
                VALUES (:id, 'default', :now, '{}')
            """), {"id": 1, "now": int(time.time() * 1000)})
            session.commit()

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
        if "test" not in str(self.db_path).lower():
            raise PermissionError("Safety check failed: clear_all can only be run on test databases.")
        with self.session_factory() as session:
            session.execute(text("PRAGMA foreign_keys = OFF"))
            for table in Base.metadata.sorted_tables:
                session.execute(table.delete())
            session.execute(text("PRAGMA foreign_keys = ON"))
            session.commit()

    def _to_dict(self, params: tuple | dict) -> dict:
        if isinstance(params, dict):
            return params
        return {f"param{i}": v for i, v in enumerate(params)}
