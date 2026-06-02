from pathlib import Path
from typing import Any

from .connection import get_connection
from .schema import init_schema


class Db:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        with get_connection(self.db_path) as con:
            init_schema(con)

    def execute(self, query: str, params: tuple = ()) -> None:
        with get_connection(self.db_path) as con:
            con.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Any:
        with get_connection(self.db_path) as con:
            return con.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple | dict = ()) -> list[Any]:
        with get_connection(self.db_path) as con:
            return con.execute(query, params).fetchall()

    def clear_all(self):
            if "test" not in str(self.db_path).lower():
                raise PermissionError("Safety check failed: clear_all can only be run on test databases.")

            tables = self.fetch_all(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )

            with get_connection(self.db_path) as con:
                con.execute("PRAGMA foreign_keys = OFF")
                for table in tables:
                    table_name = table[0]
                    con.execute(f"DELETE FROM {table_name}")
                con.execute("PRAGMA foreign_keys = ON")
                con.commit()
