import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import date
from typing import Generator, Optional, Any

class Db:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent.parent / "db.db"
        SCHEMA = """
        CREATE TABLE IF NOT EXISTS cards (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            front           TEXT NOT NULL,
            back            TEXT NOT NULL,
            deck            TEXT NOT NULL DEFAULT 'default',

            -- FSRS / SRS data
            stability       REAL NOT NULL DEFAULT 0,
            difficulty      REAL NOT NULL DEFAULT 0,
            elapsed_days    INTEGER NOT NULL DEFAULT 0,
            scheduled_days  INTEGER NOT NULL DEFAULT 0,
            reps            INTEGER NOT NULL DEFAULT 0,
            lapses          INTEGER NOT NULL DEFAULT 0,
            fsrs_state      INTEGER NOT NULL DEFAULT 0,

            -- scheduling
            last_review     TEXT,
            due_date        TEXT,

            -- metadata
            card_type       INTEGER NOT NULL DEFAULT 0,
            article_id      INTEGER,
            excerpt         TEXT,

            -- contraintes
            FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_cards_due_date ON cards(due_date);
        CREATE INDEX IF NOT EXISTS idx_cards_deck ON cards(deck);


        CREATE TABLE IF NOT EXISTS articles (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT NOT NULL,
            url       TEXT NOT NULL UNIQUE,
            source    TEXT NOT NULL DEFAULT 'wikipedia',
            added_on  TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);


        CREATE TABLE IF NOT EXISTS article_sections (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id  INTEGER NOT NULL,
            title       TEXT NOT NULL,
            body        TEXT NOT NULL,
            position    INTEGER NOT NULL,
            card_id     INTEGER,

            FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE CASCADE,
            FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_sections_article ON article_sections(article_id);
        CREATE INDEX IF NOT EXISTS idx_sections_card ON article_sections(card_id);
        """
        if not self.db_path.exists():
            self.init_db(SCHEMA)

    def _date(self, s: Optional[str]) -> Optional[date]:
        return date.fromisoformat(s) if s else None

    def _str(self, d: Optional[date]) -> Optional[str]:
        return d.isoformat() if d else None

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")

        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def init_db(self, schema: str) -> None:
        with self._conn() as con:
            con.executescript(schema)

    def execute(self, query: str, params: tuple = ()) -> None:
        with self._conn() as con:
            con.execute(query, params)

    def fetch_one(self, query: str, params: tuple = ()) -> Any:
        with self._conn() as con:
            return con.execute(query, params).fetchone()

    def fetch_all(self, query: str, params: tuple = ()) -> list[Any]:
        with self._conn() as con:
            return con.execute(query, params).fetchall()

    def create_card(self, front: str, back: str, deck: str = "default") -> int:
        with self._conn() as con:
            cur = con.execute(
                """
                INSERT INTO cards (front, back, deck)
                VALUES (?, ?, ?)
                """,
                (front, back, deck),
            )
            return cur.lastrowid

    def get_card(self, card_id: int) -> Optional[sqlite3.Row]:
        return self.fetch_one("SELECT * FROM cards WHERE id = ?", (card_id,))

    def get_all_cards(self, deck: Optional[str] = None) -> list[sqlite3.Row]:
        if deck:
            return self.fetch_all("SELECT * FROM cards WHERE deck = ?", (deck,))
        return self.fetch_all("SELECT * FROM cards")

    def update_card(self, card_id: int, **fields) -> None:
        keys = ", ".join([f"{k}=?" for k in fields])
        values = list(fields.values())

        self.execute(
            f"UPDATE cards SET {keys} WHERE id = ?",
            tuple(values + [card_id]),
        )

    def delete_card(self, card_id: int) -> None:
        self.execute("DELETE FROM cards WHERE id = ?", (card_id,))

    def count_cards(self) -> int:
        row = self.fetch_one("SELECT COUNT(*) as count FROM cards")
        return row["count"] if row else 0
