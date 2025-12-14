from __future__ import annotations

from PySide6.QtCore import QObject

from library_app.model.repository import ItemRepository
from library_app.view.main_window import MainWindow


class MainController(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._repo = ItemRepository()
        self._window = MainWindow()

        self._repo.ensure_sample_data()
        self.refresh()

        self._window.set_status("Loaded items from SQLite (Step #2).")

    def refresh(self) -> None:
        items = self._repo.list_items()
        self._window.set_items(items)

    def show(self) -> None:
        self._window.show()
