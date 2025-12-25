from __future__ import annotations

from dataclasses import dataclass

from library_app.model.enums import ItemStatus, MediaType


@dataclass(frozen=True)
class Item:
    id: int
    title: str
    media_type: MediaType
    status: ItemStatus
    rating: int | None = None
    notes: str = ""
    author: str = ""
    first_publish_year: int | None = None
    openlibrary_key: str | None = None
    cover_id: int | None = None
