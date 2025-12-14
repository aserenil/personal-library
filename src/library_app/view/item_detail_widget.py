from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from library_app.model.entities import Item


class ItemDetailWidget(QGroupBox):
    save_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Details", parent)

        self._item_id: int | None = None

        self._id_label = QLabel("—")

        self.title_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["book", "comic", "movie"])

        self.status_combo = QComboBox()
        self.status_combo.addItems(["backlog", "in_progress", "done"])

        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(0, 5)
        self.rating_spin.setSpecialValueText("None")
        self.rating_spin.setValue(0)

        self.notes_edit = QTextEdit()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_requested.emit)

        form = QFormLayout()
        form.addRow("ID", self._id_label)
        form.addRow("Title*", self.title_edit)
        form.addRow("Type", self.type_combo)
        form.addRow("Status", self.status_combo)
        form.addRow("Rating", self.rating_spin)
        form.addRow("Notes", self.notes_edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.save_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(btn_row)

        self.set_enabled(False)

    def set_enabled(self, enabled: bool) -> None:
        self.title_edit.setEnabled(enabled)
        self.type_combo.setEnabled(enabled)
        self.status_combo.setEnabled(enabled)
        self.rating_spin.setEnabled(enabled)
        self.notes_edit.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)

    def clear(self) -> None:
        self._item_id = None
        self._id_label.setText("—")
        self.title_edit.setText("")
        self.type_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.rating_spin.setValue(0)
        self.notes_edit.setPlainText("")
        self.set_enabled(False)

    def load_item(self, item: Item) -> None:
        self._item_id = item.id
        self._id_label.setText(str(item.id))
        self.title_edit.setText(item.title)
        self.type_combo.setCurrentText(item.media_type)
        self.status_combo.setCurrentText(item.status)
        self.rating_spin.setValue(0 if item.rating is None else int(item.rating))
        self.notes_edit.setPlainText(item.notes)
        self.set_enabled(True)

    def current_item_id(self) -> int | None:
        return self._item_id

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
