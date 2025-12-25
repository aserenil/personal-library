from __future__ import annotations

import sqlite3
from typing import Any, Final, cast

from library_app.model.db import connect, init_db
from library_app.model.entities import Item
from library_app.model.enums import ItemStatus, MediaType

_ITEM_COLUMNS = """
    id,
    title,
    media_type,
    status,
    rating,
    notes,
    author,
    first_publish_year,
    openlibrary_key,
    cover_id
"""

_UNSET: Final[object] = object()


class ItemRepository:
    """
    Persistence boundary (SQLite).
    """

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        # Allow injecting a test connection (e.g. sqlite3.connect(":memory:"))
        self._conn = conn if conn is not None else connect()
        init_db(self._conn)

    @staticmethod
    def _item_from_row(row: Any) -> Item:
        # DB stores enum values as strings; convert back to enums for Item.
        return Item(
            id=cast(int, row["id"]),
            title=cast(str, row["title"]),
            media_type=MediaType(cast(str, row["media_type"])),
            status=ItemStatus(cast(str, row["status"])),
            rating=cast(int | None, row["rating"]),
            notes=cast(str, row["notes"]) if row["notes"] is not None else "",
            author=cast(str, row["author"]) if row["author"] is not None else "",
            first_publish_year=cast(int | None, row["first_publish_year"]),
            openlibrary_key=cast(str | None, row["openlibrary_key"]),
            cover_id=cast(int | None, row["cover_id"]),
        )

    def list_items(self) -> list[Item]:
        rows = self._conn.execute(
            f"""
            SELECT {_ITEM_COLUMNS}
            FROM items
            ORDER BY id DESC
            """
        ).fetchall()
        return [self._item_from_row(row) for row in rows]

    def add_item(
        self,
        title: str,
        media_type: MediaType,
        status: ItemStatus,
        rating: int | None = None,
        notes: str = "",
        *,
        author: str = "",
        first_publish_year: int | None = None,
        openlibrary_key: str | None = None,
        cover_id: int | None = None,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO items (title, media_type, status, rating, notes,
                               author, first_publish_year, openlibrary_key, cover_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                media_type.value,
                status.value,
                rating,
                notes,
                author,
                first_publish_year,
                openlibrary_key,
                cover_id,
            ),
        )
        self._conn.commit()
        lastrowid = cur.lastrowid
        if lastrowid is None:
            raise RuntimeError("SQLite insert succeeded but cursor.lastrowid is None")
        return int(lastrowid)

    def get_item(self, item_id: int) -> Item | None:
        row = self._conn.execute(
            f"""
            SELECT {_ITEM_COLUMNS}
            FROM items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

        if row is None:
            return None
        return self._item_from_row(row)

    def update_item(
        self,
        item_id: int,
        *,
        title: str,
        media_type: MediaType,
        status: ItemStatus,
        rating: int | None,
        notes: str,
        author: str | None | object = _UNSET,
        first_publish_year: int | None | object = _UNSET,
        openlibrary_key: str | None | object = _UNSET,
        cover_id: int | None | object = _UNSET,
    ) -> None:
        """
        Update an item.

        Extra fields default to "keep existing" so the UI can update the basics
        without accidentally wiping author/year/cover metadata.
        """
        if (
            author is _UNSET
            or first_publish_year is _UNSET
            or openlibrary_key is _UNSET
            or cover_id is _UNSET
        ):
            existing = self.get_item(item_id)
            if existing is None:
                return  # or raise, but "no-op if missing" is fine for now

            if author is _UNSET:
                author = existing.author
            if first_publish_year is _UNSET:
                first_publish_year = existing.first_publish_year
            if openlibrary_key is _UNSET:
                openlibrary_key = existing.openlibrary_key
            if cover_id is _UNSET:
                cover_id = existing.cover_id

        self._conn.execute(
            """
            UPDATE items
            SET title = ?,
                media_type = ?,
                status = ?,
                rating = ?,
                notes = ?,
                author = ?,
                first_publish_year = ?,
                openlibrary_key = ?,
                cover_id = ?
            WHERE id = ?
            """,
            (
                title,
                media_type.value,
                status.value,
                rating,
                notes,
                cast(str | None, author),
                cast(int | None, first_publish_year),
                cast(str | None, openlibrary_key),
                cast(int | None, cover_id),
                item_id,
            ),
        )
        self._conn.commit()

    def delete_item(self, item_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self._conn.commit()
        return cur.rowcount > 0
