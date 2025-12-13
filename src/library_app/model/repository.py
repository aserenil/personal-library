from __future__ import annotations

from typing import Iterable

from library_app.model.entities import Item


class ItemRepository:
    """
    Model: persistence boundary.
    For Step #1 it's a stub. Step #2 will be SQLite.
    """

    def list_items(self) -> Iterable[Item]:
        return []
