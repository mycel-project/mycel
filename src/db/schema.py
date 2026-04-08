import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS collections (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  INTEGER NOT NULL,
    updated_at  INTEGER NOT NULL,
    conf        TEXT DEFAULT "{}",
    fsrsconf    TEXT DEFAULT "{}"
);

CREATE TABLE IF NOT EXISTS nodes (
    id              INTEGER PRIMARY KEY,
    collection_id   INTEGER NOT NULL,
    type            INTEGER NOT NULL,
    content         TEXT DEFAULT "{}",
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,
    due             INTEGER NOT NULL DEFAULT 0,

    last_review     INTEGER,
    stability       REAL,
    difficulty      REAL,
    state           INTEGER NOT NULL DEFAULT 0,
    step            INTEGER,

    priority        TEXT,
    FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_nodes_due          ON nodes(due);
CREATE INDEX IF NOT EXISTS idx_nodes_collection   ON nodes(collection_id);

CREATE TABLE IF NOT EXISTS reviews (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id         INTEGER NOT NULL,
    review_time     INTEGER NOT NULL,
    rating          INTEGER NOT NULL,
    review_type     INTEGER NOT NULL DEFAULT 0,
    interval        INTEGER NOT NULL DEFAULT 0,
    ease            REAL    NOT NULL DEFAULT 2.5,
    state_before    TEXT    NOT NULL DEFAULT '{}',
    state_after     TEXT    NOT NULL DEFAULT '{}',
    FOREIGN KEY(node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reviews_node ON reviews(node_id);
"""


def init_schema(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA)
