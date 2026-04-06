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
    order_key       TEXT,
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
    _migrate_order_key(con)


def _migrate_order_key(con: sqlite3.Connection) -> None:
    cols = {row[1] for row in con.execute("PRAGMA table_info(cards)")}
    if "order_key" not in cols:
        con.execute("ALTER TABLE cards ADD COLUMN order_key TEXT")
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_cards_order_key ON cards(order_key)"
    )

    rows = con.execute(
        "SELECT id, collection_id FROM cards WHERE order_key IS NULL ORDER BY collection_id, created_at"
    ).fetchall()
    if not rows:
        return

    from fractional_indexing import generate_key_between
    from collections import defaultdict

    by_collection: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        by_collection[row[1]].append(row[0])

    for collection_id, card_ids in by_collection.items():
        tail = con.execute(
            "SELECT MAX(order_key) FROM cards WHERE collection_id = ? AND order_key IS NOT NULL",
            (collection_id,),
        ).fetchone()
        prev_key = tail[0] if tail and tail[0] is not None else None
        for card_id in card_ids:
            new_key = generate_key_between(prev_key, None)
            con.execute("UPDATE cards SET order_key = ? WHERE id = ?", (new_key, card_id))
            prev_key = new_key
