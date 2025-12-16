from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt

from library_app.model.entities import Item


class ItemTableModel(QAbstractTableModel):
    HEADERS = ["Title", "Type", "Status", "Rating"]

    def __init__(self, items: list[Item] | None = None) -> None:
        super().__init__()
        self._items: list[Item] = items or []

    def set_items(self, items: list[Item]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._items)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:  # noqa: N802
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(
            self.HEADERS
        ):
            return self.HEADERS[section]
        return None

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = int(Qt.ItemDataRole.DisplayRole),
    ) -> Any:  # noqa: N802
        if not index.isValid():
            return None
        item = self._items[index.row()]

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            col = index.column()
            if col == 0:
                return item.title
            if col == 1:
                return item.media_type
            if col == 2:
                return item.status
            if col == 3:
                return "" if item.rating is None else str(item.rating)

        return None

    def item_at(self, row: int) -> Item | None:
        if 0 <= row < len(self._items):
            return self._items[row]
        return None
