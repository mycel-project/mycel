import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS collections (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  INTEGER NOT NULL,
    updated_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS cards (
    id              INTEGER PRIMARY KEY,
    collection_id   INTEGER NOT NULL,
    note_id         INTEGER,
    type            INTEGER NOT NULL DEFAULT 0,
    queue           INTEGER NOT NULL DEFAULT 0,
    due             INTEGER NOT NULL DEFAULT 0,
    interval        INTEGER NOT NULL DEFAULT 0,
    ease_factor     REAL    NOT NULL DEFAULT 2.5,
    stability       REAL,
    difficulty      REAL,
    fsrs_step       INTEGER,
    reps            INTEGER NOT NULL DEFAULT 0,
    lapses          INTEGER NOT NULL DEFAULT 0,
    last_review     INTEGER,
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    flags           INTEGER NOT NULL DEFAULT 0,
    data            TEXT    NOT NULL DEFAULT '{}',
    tags            TEXT    NOT NULL DEFAULT '[]',
    FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cards_due          ON cards(due);
CREATE INDEX IF NOT EXISTS idx_cards_collection   ON cards(collection_id);

CREATE TABLE IF NOT EXISTS reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id         INTEGER NOT NULL,
    review_time     INTEGER NOT NULL,
    rating          INTEGER NOT NULL,
    review_type     INTEGER NOT NULL DEFAULT 0,
    interval        INTEGER NOT NULL DEFAULT 0,
    ease            REAL    NOT NULL DEFAULT 2.5,
    state_before    TEXT    NOT NULL DEFAULT '{}',
    state_after     TEXT    NOT NULL DEFAULT '{}',
    FOREIGN KEY(card_id) REFERENCES cards(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reviews_card ON reviews(card_id);
"""


def init_schema(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA)
