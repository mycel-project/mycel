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
    parent_id       INTEGER,
    type            INTEGER NOT NULL,
    content         TEXT DEFAULT "{}",
    created_at      INTEGER NOT NULL,
    updated_at      INTEGER NOT NULL,

    state           INTEGER NOT NULL DEFAULT 0,
    step            INTEGER,
    stability       REAL,
    difficulty      REAL,
    due             INTEGER NOT NULL DEFAULT 0,
    last_review     INTEGER,

    priority        TEXT,
    FOREIGN KEY(collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reviews (
    id              INTEGER PRIMARY KEY,
    node_id         INTEGER NOT NULL,
    time     INTEGER NOT NULL,
    duration     INTEGER NOT NULL,
    rating          INTEGER NOT NULL,

    FOREIGN KEY(node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_nodes_due          ON nodes(due);
CREATE INDEX IF NOT EXISTS idx_nodes_collection   ON nodes(collection_id);
CREATE INDEX IF NOT EXISTS idx_reviews_node ON reviews(node_id);
"""


def init_schema(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA)
