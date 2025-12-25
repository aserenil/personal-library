from library_app.model.enums import ItemStatus, MediaType
from library_app.model.repository import ItemRepository


def _ensure_sample_data(repo: ItemRepository) -> None:
    if repo.list_items():
        return
    repo.add_item(
        title="The Hobbit",
        media_type=MediaType.BOOK,
        status=ItemStatus.DONE,
        rating=5,
        notes="Sample item",
        author="J.R.R. Tolkien",
        first_publish_year=1937,
    )
