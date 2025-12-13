from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QToolBar,
    QStatusBar,
)


class MainWindow(QMainWindow):
    """
    View: contains Qt widgets only.
    No DB calls, no HTTP calls.
    """

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

        self._headline = QLabel("Personal Library — Step #1 (UI Skeleton)")
        self._headline.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self._headline)

        self._hint = QLabel("Next: SQLite + Table View + Add/Search flow.")
        layout.addWidget(self._hint)

        self.setCentralWidget(root)

    def set_status(self, text: str) -> None:
        self._status.showMessage(text)
