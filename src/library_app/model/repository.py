from __future__ import annotations

from library_app.model.db import connect, init_db
from library_app.model.entities import Item


class ItemRepository:
    """
    Persistence boundary (SQLite).
    """

    def __init__(self) -> None:
        self._conn = connect()
        init_db(self._conn)

    def list_items(self) -> list[Item]:
        rows = self._conn.execute(
            "SELECT id, title, media_type, status, rating, notes FROM items ORDER BY id DESC"
        ).fetchall()
        return [
            Item(
                id=row["id"],
                title=row["title"],
                media_type=row["media_type"],
                status=row["status"],
                rating=row["rating"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def add_item(
        self,
        title: str,
        media_type: str = "book",
        status: str = "backlog",
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
                media_type,
                status,
                rating,
                notes,
                author,
                first_publish_year,
                openlibrary_key,
                cover_id,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def get_item(self, item_id: int) -> Item | None:
        row = self._conn.execute(
            """
            SELECT id,
                   title,
                   media_type,
                   status,
                   rating,
                   notes,
                   author,
                   first_publish_year,
                   openlibrary_key,
                   cover_id
            FROM items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

        if row is None:
            return None

        return Item(
            id=row["id"],
            title=row["title"],
            media_type=row["media_type"],
            status=row["status"],
            rating=row["rating"],
            notes=row["notes"],
            author=row["author"],
            first_publish_year=row["first_publish_year"],
            openlibrary_key=row["openlibrary_key"],
            cover_id=row["cover_id"],
        )

    def update_item(
        self,
        item_id: int,
        *,
        title: str,
        media_type: str,
        status: str,
        rating: int | None,
        notes: str,
    ) -> None:
        self._conn.execute(
            """
            UPDATE items
            SET title = ?, media_type = ?, status = ?, rating = ?, notes = ?
            WHERE id = ?
            """,
            (title, media_type, status, rating, notes, item_id),
        )
        self._conn.commit()

    def ensure_sample_data(self) -> None:
        count = self._conn.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"]
        if count:
            return
        self.add_item("The Hobbit", media_type="book", status="done", rating=5)
        self.add_item("Amazing Spider-Man #1", media_type="comic", status="backlog")
        self.add_item("The Social Network", media_type="movie", status="done", rating=4)
