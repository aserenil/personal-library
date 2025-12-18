from __future__ import annotations

from collections import OrderedDict
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
)
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap

from library_app.model.covers import cached_cover_path
from library_app.model.entities import Item


class ItemTableModel(QAbstractTableModel):
    HEADERS = ["Title", "Type", "Status", "Rating"]
    cover_requested = Signal(int)  # cover_id
    _THUMB_W = 32
    _THUMB_H = 48

    def __init__(self, items: list[Item] | None = None) -> None:
        super().__init__()
        self._items: list[Item] = items or []
        self._thumb_loading = self._make_placeholder("…")
        self._thumb_missing = self._make_placeholder("×")
        self._cover_requested: set[int] = set()
        self._cover_failed: set[int] = set()
        self._pix_lru: OrderedDict[int, QPixmap] = OrderedDict()
        self._pix_lru_max = 128  # tweak later if you want

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

        # Thumbnail in Title column
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            cover_id = item.cover_id
            if not cover_id:
                return None  # or: return self._thumb_missing

            # LRU hit
            pix = self._lru_get(cover_id)
            if pix is not None:
                return pix

            # 2. Failed cover → permanent placeholder
            if cover_id in self._cover_failed:
                return self._thumb_missing

            path = cached_cover_path(cover_id, size="M")
            if path.exists() and path.stat().st_size > 0:
                pix = QPixmap(str(path))
                if not pix.isNull():
                    pix = pix.scaled(
                        self._THUMB_W,
                        self._THUMB_H,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self._lru_put(cover_id, pix)
                    return pix

            # Request once, show loading placeholder
            if cover_id not in self._cover_requested:
                self._cover_requested.add(cover_id)
                self.cover_requested.emit(cover_id)

            return self._thumb_loading

        return None

    def item_at(self, row: int) -> Item | None:
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    def set_cover_ready(self, cover_id: int, ok: bool) -> None:
        if not ok:
            self._cover_failed.add(cover_id)

        # refresh rows that use this cover_id
        self._pix_lru.pop(cover_id, None)
        for row, item in enumerate(self._items):
            if item.cover_id == cover_id:
                idx = self.index(row, 0)
                self.dataChanged.emit(idx, idx, [int(Qt.ItemDataRole.DecorationRole)])

    def _make_placeholder(self, mark: str) -> QPixmap:
        pix = QPixmap(self._THUMB_W, self._THUMB_H)
        pix.fill(Qt.GlobalColor.transparent)

        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # simple “book card”
        rect = pix.rect().adjusted(1, 1, -1, -1)
        p.setPen(QPen(QColor(150, 150, 150)))
        p.setBrush(QBrush(QColor(60, 60, 60)))  # looks fine in dark mode too
        p.drawRoundedRect(rect, 4, 4)

        # mark in the center
        p.setPen(QPen(QColor(230, 230, 230)))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, mark)

        p.end()
        return pix

    def _lru_get(self, cover_id: int) -> QPixmap | None:
        pix = self._pix_lru.get(cover_id)
        if pix is None:
            return None
        # mark as recently used
        self._pix_lru.move_to_end(cover_id)
        return pix

    def _lru_put(self, cover_id: int, pix: QPixmap) -> None:
        self._pix_lru[cover_id] = pix
        self._pix_lru.move_to_end(cover_id)
        while len(self._pix_lru) > self._pix_lru_max:
            self._pix_lru.popitem(last=False)  # evict least-recently-used
