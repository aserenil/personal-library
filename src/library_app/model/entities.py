from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    id: int
    title: str
    media_type: str  # later: Enum (book/comic/movie/etc)
    status: str      # later: Enum (backlog/in_progress/done)
    rating: int | None = None
    notes: str = ""
