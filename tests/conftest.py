# tests/conftest.py
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest


def _apply_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    conn.commit()


@pytest.fixture()
def db_conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # point this at your real schema.sql (adjust path if needed)
    schema_path = Path(__file__).resolve().parents[1] / "schema.sql"
    _apply_schema(conn, schema_path)

    yield conn
    conn.close()
