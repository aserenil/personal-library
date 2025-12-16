from __future__ import annotations

from enum import Enum


class MediaType(Enum):
    BOOK = "book"
    COMIC = "comic"
    MOVIE = "movie"


class ItemStatus(Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    DONE = "done"
