# tests/test_repository.py
from __future__ import annotations

import sqlite3

from library_app.model.enums import ItemStatus, MediaType
from library_app.model.repository import ItemRepository


def test_add_and_get_item(db_conn: sqlite3.Connection) -> None:
    repo = ItemRepository(db_conn)

    new_id = repo.add_item(
        title="The Hobbit",
        media_type=MediaType.BOOK,
        status=ItemStatus.DONE,
        rating=5,
        notes="classic",
        author="J.R.R. Tolkien",
        first_publish_year=1937,
        openlibrary_key="/works/OL262758W",
        cover_id=1234,
    )
    assert isinstance(new_id, int)

    item = repo.get_item(new_id)
    assert item is not None
    assert item.id == new_id
    assert item.title == "The Hobbit"
    assert item.media_type == MediaType.BOOK
    assert item.status == ItemStatus.DONE
    assert item.rating == 5


def test_list_items_sorted_desc(db_conn: sqlite3.Connection) -> None:
    repo = ItemRepository(db_conn)

    id1 = repo.add_item(title="A", media_type=MediaType.BOOK, status=ItemStatus.DONE)
    id2 = repo.add_item(title="B", media_type=MediaType.BOOK, status=ItemStatus.DONE)

    items = repo.list_items()
    assert [i.id for i in items][:2] == [id2, id1]


def test_update_item(db_conn: sqlite3.Connection) -> None:
    repo = ItemRepository(db_conn)
    item_id = repo.add_item(
        title="Old", media_type=MediaType.BOOK, status=ItemStatus.BACKLOG
    )

    repo.update_item(
        item_id,
        title="New",
        media_type=MediaType.COMIC,
        status=ItemStatus.IN_PROGRESS,
        rating=3,
        notes="updated",
        author="Someone",
        first_publish_year=2000,
        openlibrary_key="/works/OLxxx",
        cover_id=999,
    )

    item = repo.get_item(item_id)
    assert item is not None
    assert item.title == "New"
    assert item.media_type == MediaType.COMIC
    assert item.status == ItemStatus.IN_PROGRESS
    assert item.rating == 3


def test_delete_item(db_conn: sqlite3.Connection) -> None:
    repo = ItemRepository(db_conn)
    item_id = repo.add_item(
        title="Delete me", media_type=MediaType.BOOK, status=ItemStatus.DONE
    )

    repo.delete_item(item_id)
    assert repo.get_item(item_id) is None
