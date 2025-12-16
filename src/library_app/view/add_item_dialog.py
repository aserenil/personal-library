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
    QWidget,
)

from library_app.model.enums import ItemStatus, MediaType
from library_app.view.types import ItemFormData


class AddItemDialog(QDialog):
    """
    View-only dialog. Collects user input; does NOT write to DB.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Item")
        self.setModal(True)
        self.resize(420, 280)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g. The Hobbit")

        self.type_combo = QComboBox()
        self.type_combo.clear()
        for mt in MediaType:
            self.type_combo.addItem(mt.value, mt)

        self.status_combo = QComboBox()
        self.status_combo.clear()
        for st in ItemStatus:
            self.status_combo.addItem(st.value, st)

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

        buttons = QDialogButtonBox(self)
        buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self.title_edit.setFocus()

    def _collect_form_data(self) -> ItemFormData:
        rating_val = self.rating_spin.value()
        rating = None if rating_val == 0 else rating_val

        media_type = self.type_combo.currentData()
        status = self.status_combo.currentData()

        return ItemFormData(
            title=self.title_edit.text().strip(),
            media_type=media_type,
            status=status,
            rating=rating,
            notes=self.notes_edit.toPlainText().strip(),
        )

    def get_data(self) -> ItemFormData:
        return self._collect_form_data()
