from __future__ import annotations

from pathlib import Path

import httpx


def _project_root() -> Path:
    # covers.py -> model -> library_app -> src -> project root
    return Path(__file__).resolve().parents[3]


def cover_cache_dir() -> Path:
    d = _project_root() / "data" / "covers"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cover_url(cover_id: int, *, size: str = "M") -> str:
    # Open Library Covers API: https://covers.openlibrary.org/
    # size: S, M, L
    return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"


def cached_cover_path(cover_id: int, *, size: str = "M") -> Path:
    return cover_cache_dir() / f"{cover_id}-{size}.jpg"


def fetch_cover_to_cache(cover_id: int, *, size: str = "M") -> Path | None:
    """
    Returns a local file path to a cached cover image.
    Downloads from Open Library only if missing.
    """
    path = cached_cover_path(cover_id, size=size)
    if path.exists() and path.stat().st_size > 0:
        return path

    url = cover_url(cover_id, size=size)
    tmp = path.with_suffix(path.suffix + ".tmp")

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            r = client.get(url)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            tmp.write_bytes(r.content)
        tmp.replace(path)
        return path
    except Exception:
        # best-effort cache; controller can just show "No cover"
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
        return None
