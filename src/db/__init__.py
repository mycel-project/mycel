from pathlib import Path
from typing import Any

from .connection import get_connection
from .schema import init_schema


class Db:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent.parent.parent / "db.db"
        with get_connection(self.db_path) as con:
            init_schema(con)

    def execute(self, query: str, params: tuple = ()) -> None:
        with get_connection(self.db_path) as con:
            con.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Any:
        with get_connection(self.db_path) as con:
            return con.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> list[Any]:
        with get_connection(self.db_path) as con:
            return con.execute(query, params).fetchall()

    def execute_returning(self, query: str, params: tuple = ()) -> int:
        with get_connection(self.db_path) as con:
            cur = con.execute(query, params)
            return cur.lastrowid or 0
