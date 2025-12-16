from typing import TypedDict


class ItemFormData(TypedDict):
    title: str
    media_type: str
    status: str
    rating: int | None
    notes: str
