from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class OLResult:
    key: str  # e.g. "/works/OL82563W"
    title: str
    author: str
    first_publish_year: int | None
    edition_count: int | None
    cover_i: int | None  # used for covers API


def search_openlibrary(query: str, *, limit: int = 25) -> list[OLResult]:
    query = query.strip()
    if not query:
        return []

    # Use explicit fields (Open Library changed /search.json defaults in 2025)
    # https://openlibrary.org/search.json?q=...
    params = {
        "q": query,
        "limit": str(limit),
        "fields": "key,title,author_name,first_publish_year,edition_count,cover_i",
    }

    with httpx.Client(timeout=10.0) as client:
        r = client.get("https://openlibrary.org/search.json", params=params)
        r.raise_for_status()
        data: dict[str, Any] = r.json()

    docs = data.get("docs", [])
    out: list[OLResult] = []
    for d in docs:
        authors = d.get("author_name") or []
        author = authors[0] if authors else ""
        out.append(
            OLResult(
                key=d.get("key", ""),
                title=d.get("title", "") or "",
                author=author or "",
                first_publish_year=d.get("first_publish_year"),
                edition_count=d.get("edition_count"),
                cover_i=d.get("cover_i"),
            )
        )
    return out
