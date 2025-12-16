from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: int
    title: str
    media_type: str  # book/comic/movie/etc (later: Enum)
    status: str  # backlog/in_progress/done (later: Enum)
    rating: int | None = None
    notes: str = ""
    author: str = ""
    first_publish_year: int | None = None
    openlibrary_key: str | None = None
    cover_id: int | None = None
