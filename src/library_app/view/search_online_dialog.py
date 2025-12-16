from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from library_app.model.openlibrary import OLResult


class SearchOnlineDialog(QDialog):
    search_requested = Signal(str)
    import_requested = Signal(object)  # OLResult

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Search Online (Open Library)")
        self.resize(820, 420)

        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("Search books (e.g. The Hobbit)")

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(
            lambda: self.search_requested.emit(self.query_edit.text())
        )

        top = QHBoxLayout()
        top.addWidget(QLabel("Query:"))
        top.addWidget(self.query_edit, 1)
        top.addWidget(self.search_btn)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Title", "Author", "Year", "Editions", "Key"]
        )
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)

        self.import_btn = QPushButton("Add Selected")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._on_import)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.import_btn)

        self._results: list[OLResult] = []
        self.query_edit.setFocus()

    def set_busy(self, busy: bool) -> None:
        self.search_btn.setEnabled(not busy)
        self.query_edit.setEnabled(not busy)

    def set_results(self, results: list[OLResult]) -> None:
        self._results = results
        self.table.setRowCount(0)
        for r in results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(r.title))
            self.table.setItem(row, 1, QTableWidgetItem(r.author))
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    "" if r.first_publish_year is None else str(r.first_publish_year)
                ),
            )
            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    "" if r.edition_count is None else str(r.edition_count)
                ),
            )
            self.table.setItem(row, 4, QTableWidgetItem(r.key))
        self.import_btn.setEnabled(False)

    def _on_selection_changed(self) -> None:
        self.import_btn.setEnabled(len(self.table.selectedItems()) > 0)

    def _on_import(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._results):
            return
        self.import_requested.emit(self._results[row])
