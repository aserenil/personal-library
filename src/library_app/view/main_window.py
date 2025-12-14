from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QToolBar,
    QStatusBar,
    QSplitter,
    QTableView,
)

from library_app.view.item_table_model import ItemTableModel
from library_app.view.item_detail_widget import ItemDetailWidget


class MainWindow(QMainWindow):
    add_item_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        ...
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        add_action = QAction("Add", self)
        add_action.setToolTip("Add a new item")
        add_action.triggered.connect(self.add_item_requested.emit)
        toolbar.addAction(add_action)

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

        self.detail = ItemDetailWidget(self)

        splitter.addWidget(self.table)
        splitter.addWidget(self.detail)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        self._model = ItemTableModel([])
        self.table.setModel(self._model)

        self.setCentralWidget(root)

    def set_status(self, text: str) -> None:
        self._status.showMessage(text)

    def set_items(self, items) -> None:
        self._model.set_items(items)
        self.table.resizeColumnsToContents()
