from __future__ import annotations

from PySide6.QtCore import QObject

from library_app.model.repository import ItemRepository
from library_app.view.main_window import MainWindow


class MainController(QObject):
    """
    Controller: wires the UI to the model layer.
    For Step #1, it's just bootstrapping + a stub repository.
    """

    def __init__(self) -> None:
        super().__init__()
        self._repo = ItemRepository()
        self._window = MainWindow()

        # Example: controller sets initial UI state
        self._window.set_status("Ready. (Step #1)")

    def show(self) -> None:
        self._window.show()
