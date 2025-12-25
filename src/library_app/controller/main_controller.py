from __future__ import annotations

import os
from pathlib import Path
from typing import cast

from PySide6.QtCore import QObject, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QMessageBox

from library_app.dev.seed import _ensure_sample_data
from library_app.model.covers import fetch_cover_to_cache
from library_app.model.entities import Item
from library_app.model.enums import ItemStatus, MediaType
from library_app.model.openlibrary import OLResult, search_openlibrary
from library_app.model.repository import ItemRepository
from library_app.util.worker import Worker
from library_app.view.add_item_dialog import AddItemDialog
from library_app.view.item_table_model import ItemTableModel
from library_app.view.main_window import MainWindow
from library_app.view.search_online_dialog import SearchOnlineDialog


class MainController(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._repo = ItemRepository()
        self._window = MainWindow()
        self.table_model: ItemTableModel = self._window.table_model
        self.table_model.cover_requested.connect(self._on_cover_requested)

        self._current_cover_item_id: int | None = None
        self._current_cover_cover_id: int | None = None

        if os.environ.get("LIBRARY_DEV_SEED") == "1":
            _ensure_sample_data(self._repo)

        self.refresh()

        self._window.add_item_requested.connect(self.on_add_item)

        # selection -> detail
        self._window.table.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

        # detail save -> repo update
        self._window.detail.save_requested.connect(self.on_save_item)

        self._window.delete_action.triggered.connect(self.on_delete_item)

        self._pool = QThreadPool.globalInstance()
        self._window.search_online_requested.connect(self.on_search_online)

        # when wiring things up:
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self._shutdown)

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
                    idx = self.table_model.index(row, 0)
                    self._window.table.selectRow(row)
                    self._window.table.scrollTo(idx)
                    break

    def selected_item_id(self) -> int | None:
        index = self._window.table.currentIndex()
        if not index.isValid():
            return None
        item = self.table_model.item_at(index.row())  # from ItemTableModel
        return None if item is None else item.id

    def on_selection_changed(self, *_args: object) -> None:
        item_id = self.selected_item_id()
        if item_id is None:
            self._window.detail.clear()
            return

        item = self._repo.get_item(item_id)
        if item is None:
            self._window.detail.clear()
            return

        self._window.detail.load_item(item)
        self._load_cover_for_item(item)
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

        media_type = data["media_type"]
        status = data["status"]

        self._repo.update_item(
            item_id=item_id,
            title=title,
            media_type=media_type,
            status=status,
            rating=data["rating"],
            notes=data["notes"],
        )
        self.refresh(reselect_id=item_id)
        self._window.set_status(f"Saved: {title}")

    def on_add_item(self) -> None:
        dlg = AddItemDialog(self._window)
        from PySide6.QtWidgets import QDialog

        if dlg.exec() != QDialog.DialogCode.Accepted:
            self._window.set_status("Add cancelled.")
            return

        data = dlg.get_data()
        title = str(data["title"])
        if not title:
            self._window.set_status("Title is required.")
            return

        new_id = self._repo.add_item(
            title=title,
            media_type=data["media_type"],
            status=data["status"],
            rating=data["rating"],
            notes=str(data["notes"]),
        )
        self.refresh(reselect_id=new_id)
        self._window.set_status(f"Added: {title}")

    def on_search_online(self) -> None:
        dlg = SearchOnlineDialog(self._window)
        dlg.search_requested.connect(lambda q: self._do_search(dlg, q))
        dlg.import_requested.connect(lambda r: self._import_result(dlg, r))
        dlg.exec()

    def _do_search(self, dlg: SearchOnlineDialog, query: str) -> None:
        dlg.set_busy(True)
        self._window.set_status("Searching Open Library...")

        w = Worker(search_openlibrary, query, limit=25)
        w.signals.result.connect(lambda results: dlg.set_results(results))
        w.signals.error.connect(self._on_search_error)
        w.signals.finished.connect(lambda: dlg.set_busy(False))
        w.signals.result.connect(lambda _: self._window.set_status("Search complete."))
        self._pool.start(cast(QRunnable, w))

    def _on_search_error(self, tb: str) -> None:
        self._window.set_status("Search failed (see console).")
        print(tb)

    def _import_result(self, dlg: SearchOnlineDialog, r: OLResult) -> None:
        if not r.title:
            self._window.set_status("Cannot import empty title.")
            return

        new_id = self._repo.add_item(
            title=r.title,
            media_type=MediaType.BOOK,
            status=ItemStatus.BACKLOG,
            rating=None,
            notes="Imported from Open Library",
            author=r.author,
            first_publish_year=r.first_publish_year,
            openlibrary_key=r.key or None,
            cover_id=r.cover_i,
        )
        self.refresh(reselect_id=new_id)
        self._window.set_status(f"Imported: {r.title}")
        dlg.accept()

    def _load_cover_for_item(self, item: Item) -> None:
        # Guard against races when clicking around quickly
        self._current_cover_item_id = item.id
        self._current_cover_cover_id = item.cover_id

        cover_id = item.cover_id
        if not cover_id:
            self._window.detail.set_cover_path(None)
            return

        w = Worker(fetch_cover_to_cache, cover_id, size="M")
        w.signals.result.connect(lambda p: self._on_cover_ready(item.id, cover_id, p))
        w.signals.error.connect(lambda tb: print(tb))
        self._pool.start(cast(QRunnable, w))

    def _on_cover_ready(self, item_id: int, cover_id: int, path: Path | None) -> None:
        # Only update UI if we're still on the same selected item/cover
        if self._current_cover_item_id != item_id:
            return
        if self._current_cover_cover_id != cover_id:
            return

        # Worker returns Path | None; keep it simple
        self._window.detail.set_cover_path(path)

    def _on_cover_requested(self, cover_id: int) -> None:
        w = Worker(fetch_cover_to_cache, cover_id, size="M")

        def _done(p: Path | None) -> None:
            self.table_model.set_cover_ready(cover_id, ok=(p is not None))

        def _err(tb: str) -> None:
            print(tb)
            self.table_model.set_cover_ready(cover_id, ok=False)

        w.signals.result.connect(_done)
        w.signals.error.connect(_err)
        self._pool.start(cast(QRunnable, w))

    def on_delete_item(self) -> None:
        item_id = self._window.selected_item_id()
        if item_id is None:
            self._window.set_status("Select an item to delete.")
            return

        item = self._repo.get_item(item_id)
        title = item.title if item else f"item #{item_id}"

        btn = QMessageBox.question(
            self._window,
            "Delete item",
            f"Delete {title} (#{item_id})? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if btn != QMessageBox.StandardButton.Yes:
            return

        deleted = self._repo.delete_item(item_id)
        if not deleted:
            self._window.set_status("Item was not found (already deleted?).")
            return

        # Refresh list + clear details (selection might now be invalid)
        self.refresh()
        self._window.detail.clear()
        self._window.set_status(f"Deleted {title} (#{item_id}).")

    def _shutdown(self) -> None:
        # stop scheduling new work first (optional flag)
        self._pool.waitForDone(2000)  # milliseconds; bump if you want
