from typing import TypedDict

from library_app.model.enums import ItemStatus, MediaType


class ItemFormData(TypedDict):
    title: str
    media_type: MediaType
    status: ItemStatus
    rating: int | None
    notes: str
