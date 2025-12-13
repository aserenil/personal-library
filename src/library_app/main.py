from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication

from library_app.controller.main_controller import MainController


def main() -> int:
    app = QApplication(sys.argv)

    controller = MainController()
    controller.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
