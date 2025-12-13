from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QToolBar,
    QStatusBar,
    QTableView,
)

from library_app.view.item_table_model import ItemTableModel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Personal Library (MVC Learning App)")
        self.resize(1000, 650)

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        root = QWidget(self)
        layout = QVBoxLayout(root)

        self._headline = QLabel("Personal Library — Step #2 (SQLite + QTableView)")
        self._headline.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self._headline)

        self.table = QTableView(self)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

        self._model = ItemTableModel([])
        self.table.setModel(self._model)

        self.setCentralWidget(root)

    def set_status(self, text: str) -> None:
        self._status.showMessage(text)

    def set_items(self, items) -> None:
        self._model.set_items(items)
        self.table.resizeColumnsToContents()
