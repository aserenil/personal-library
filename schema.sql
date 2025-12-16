-- schema.sql
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    media_type TEXT NOT NULL,
    status TEXT NOT NULL,
    rating INTEGER NULL,
    notes TEXT NOT NULL DEFAULT '',
    author TEXT NOT NULL DEFAULT '',
    first_publish_year INTEGER NULL,
    openlibrary_key TEXT UNIQUE,
    cover_id INTEGER NULL
);
