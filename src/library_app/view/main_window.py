from __future__ import annotations

from typing import cast

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from library_app.model.entities import Item
from library_app.view.item_detail_widget import ItemDetailWidget
from library_app.view.item_table_model import ItemTableModel

THUMB_W = 32
THUMB_H = 48
ROW_H = THUMB_H + 6  # padding so it doesn’t touch borders


class MainWindow(QMainWindow):
    add_item_requested = Signal()
    search_online_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        ...
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        self.add_action = QAction("Add", self)
        self.add_action.setToolTip("Add a new item")
        self.add_action.triggered.connect(self.add_item_requested.emit)

        self.search_action = QAction("Search Online", self)
        self.search_action.triggered.connect(self.search_online_requested.emit)

        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.setStatusTip("Delete the selected item")
        self.delete_action.setEnabled(False)  # only enable when a row is selected

        menu = self.menuBar().addMenu("Actions")
        menu.addAction(self.add_action)
        menu.addAction(self.search_action)
        menu.addSeparator()
        menu.addAction(self.delete_action)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        root = QWidget(self)
        layout = QVBoxLayout(root)

        self._headline = QLabel("Personal Library — Step #2 (SQLite + QTableView)")
        self._headline.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self._headline)

        splitter = QSplitter(self)
        splitter.setChildrenCollapsible(False)

        self.table = QTableView(self)
        self.table.setSortingEnabled(True)
        self.table.setIconSize(QSize(THUMB_W, THUMB_H))
        self.table.verticalHeader().setDefaultSectionSize(ROW_H)
        vh = self.table.verticalHeader()
        vh.setDefaultSectionSize(ROW_H)
        vh.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # keeps them fixed
        self.table.verticalHeader().setVisible(False)  # hides row numbers
        self.table.setWordWrap(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.detail = ItemDetailWidget(self)

        splitter.addWidget(self.table)
        splitter.addWidget(self.detail)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        self.table_model = ItemTableModel([])
        self.table.setModel(self.table_model)

        self.table.selectionModel().selectionChanged.connect(
            lambda *_: self._on_selection_changed()
        )

        self.setCentralWidget(root)

    def set_status(self, text: str) -> None:
        self._status.showMessage(text)

    def set_items(self, items: list[Item]) -> None:
        self.table_model.set_items(items)
        self.table.resizeColumnsToContents()

    def _on_selection_changed(self) -> None:
        self.delete_action.setEnabled(self.selected_item_id() is not None)

    def selected_item_id(self) -> int | None:
        sel = self.table.selectionModel()
        if sel is None:
            return None

        rows = sel.selectedRows()
        if not rows:
            return None

        model = cast(ItemTableModel, self.table.model())
        item = model.item_at(rows[0].row())
        return item.id if item else None
