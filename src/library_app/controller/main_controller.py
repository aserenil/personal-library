from __future__ import annotations

from PySide6.QtCore import QObject

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

        # selection -> detail
        self._window.table.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # detail save -> repo update
        self._window.detail.save_requested.connect(self.on_save_item)

        self._window.set_status("Loaded items from SQLite.")

    def show(self) -> None:
        self._window.show()

    def refresh(self, *, reselect_id: int | None = None) -> None:
        items = self._repo.list_items()
        self._window.set_items(items)

        if reselect_id is not None:
            # reselect row by id after refresh (keeps UI stable)
            for row, item in enumerate(items):
                if item.id == reselect_id:
                    idx = self._window.table.model().index(row, 0)
                    self._window.table.selectRow(row)
                    self._window.table.scrollTo(idx)
                    break

    def selected_item_id(self) -> int | None:
        index = self._window.table.currentIndex()
        if not index.isValid():
            return None
        item = self._window.table.model().item_at(index.row())  # from ItemTableModel
        return None if item is None else item.id

    def on_selection_changed(self, *_args) -> None:
        item_id = self.selected_item_id()
        if item_id is None:
            self._window.detail.clear()
            return

        item = self._repo.get_item(item_id)
        if item is None:
            self._window.detail.clear()
            return

        self._window.detail.load_item(item)
        self._window.set_status(f"Selected: {item.title}")

    def on_save_item(self) -> None:
        item_id = self._window.detail.current_item_id()
        if item_id is None:
            self._window.set_status("Nothing selected.")
            return

        data = self._window.detail.get_data()
        title = str(data["title"])
        if not title:
            self._window.set_status("Title is required.")
            return

        self._repo.update_item(
            item_id,
            title=title,
            media_type=str(data["media_type"]),
            status=str(data["status"]),
            rating=data["rating"],  # int | None
            notes=str(data["notes"]),
        )
        self.refresh(reselect_id=item_id)
        self._window.set_status(f"Saved: {title}")

    def on_add_item(self) -> None:
        dlg = AddItemDialog(self._window)
        from PySide6.QtWidgets import QDialog

        if dlg.exec() != QDialog.Accepted:
            self._window.set_status("Add cancelled.")
            return

        data = dlg.get_data()
        title = str(data["title"])
        if not title:
            self._window.set_status("Title is required.")
            return

        new_id = self._repo.add_item(
            title=title,
            media_type=str(data["media_type"]),
            status=str(data["status"]),
            rating=data["rating"],
            notes=str(data["notes"]),
        )
        self.refresh(reselect_id=new_id)
        self._window.set_status(f"Added: {title}")
