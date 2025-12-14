from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)


class AddItemDialog(QDialog):
    """
    View-only dialog. Collects user input; does NOT write to DB.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Item")
        self.setModal(True)
        self.resize(420, 280)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g. The Hobbit")

        self.type_combo = QComboBox()
        self.type_combo.addItems(["book", "comic", "movie"])

        self.status_combo = QComboBox()
        self.status_combo.addItems(["backlog", "in_progress", "done"])

        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(0, 5)
        self.rating_spin.setSpecialValueText("None")  # 0 will mean None
        self.rating_spin.setValue(0)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Optional notes...")

        form = QFormLayout()
        form.addRow("Title*", self.title_edit)
        form.addRow("Type", self.type_combo)
        form.addRow("Status", self.status_combo)
        form.addRow("Rating", self.rating_spin)
        form.addRow("Notes", self.notes_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.title_edit.setFocus()

    def get_data(self) -> dict[str, object]:
        rating_val = self.rating_spin.value()
        rating = None if rating_val == 0 else rating_val
        return {
            "title": self.title_edit.text().strip(),
            "media_type": self.type_combo.currentText(),
            "status": self.status_combo.currentText(),
            "rating": rating,
            "notes": self.notes_edit.toPlainText().strip(),
        }
