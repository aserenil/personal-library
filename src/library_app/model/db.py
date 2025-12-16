from __future__ import annotations

import sqlite3
from pathlib import Path

# NOTE: DB path currently depends on working directory.
# For production / tests, consider anchoring to project root.
# Simple, explicit location for learning purposes:
# personal-library/data/library.db
DB_PATH = Path.cwd() / "data" / "library.db"


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            media_type TEXT NOT NULL,
            status TEXT NOT NULL,
            rating INTEGER NULL,
            notes TEXT NOT NULL DEFAULT ''
        );
        """
    )
    # Lightweight "migration": add columns if missing
    for stmt in [
        "ALTER TABLE items ADD COLUMN openlibrary_key TEXT NULL",
        "ALTER TABLE items ADD COLUMN cover_id INTEGER NULL",
        "ALTER TABLE items ADD COLUMN author TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE items ADD COLUMN first_publish_year INTEGER NULL",
    ]:
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise

    conn.commit()
