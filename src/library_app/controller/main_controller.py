from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from library_app.model.repository import ItemRepository
from library_app.view.main_window import MainWindow
from library_app.view.add_item_dialog import AddItemDialog


class MainController(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._repo = ItemRepository()
        self._window = MainWindow()

        self._repo.ensure_sample_data()
        self.refresh()

        self._window.add_item_requested.connect(self.on_add_item)

        self._window.set_status("Loaded items from SQLite.")

    def on_add_item(self) -> None:
        dlg = AddItemDialog(self._window)
        if dlg.exec() != QDialog.Accepted:
            self._window.set_status("Add cancelled.")
            return

        data = dlg.get_data()
        title = str(data["title"])
        if not title:
            self._window.set_status("Title is required.")
            return

        self._repo.add_item(
            title=title,
            media_type=str(data["media_type"]),
            status=str(data["status"]),
            rating=data["rating"],  # int | None
            notes=str(data["notes"]),
        )
        self.refresh()
        self._window.set_status(f"Added: {title}")

    def refresh(self) -> None:
        items = self._repo.list_items()
        self._window.set_items(items)

    def show(self) -> None:
        self._window.show()
