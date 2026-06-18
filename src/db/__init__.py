import os
import time
from typing import Any
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine.create import event
from sqlalchemy.orm import sessionmaker

from src.utils.env import is_testing
from .schema import Base
from .models import *
from dotenv import load_dotenv

load_dotenv()

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in type(dbapi_connection).__module__.lower():
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

class Db:
    def __init__(self, db_path: str):
        self.testing = is_testing()
        db_path = os.getenv("DATABASE_URL") or db_path
        self.db_path = db_path
        if str(db_path).startswith("postgresql"):
            url = str(db_path)
        else:
            url = f"sqlite:///{db_path}"
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

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

    def execute_transaction(self, statements: list[tuple[str, dict]]) -> None:
        with self.session_factory() as session:
            with session.begin():
                for query, params in statements:
                    session.execute(text(query), self._to_dict(params))
            
    def _to_dict(self, params: tuple | dict) -> dict:
        if isinstance(params, dict):
            return params
        return {f"param{i}": v for i, v in enumerate(params)}
