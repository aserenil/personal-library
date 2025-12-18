from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
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
from library_app.model.enums import ItemStatus, MediaType
from library_app.view.types import ItemFormData


class ItemDetailWidget(QGroupBox):
    save_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Details", parent)

        self._item_id: int | None = None

        self._id_label = QLabel("—")

        self.title_edit = QLineEdit()

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
        self.rating_spin.setSpecialValueText("None")
        self.rating_spin.setValue(0)

        self.notes_edit = QTextEdit()

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_requested.emit)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.cover_label.setMinimumHeight(220)
        self.cover_label.setText("No cover")

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
        layout.addWidget(self.cover_label)
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
        self.clear_cover()
        self.set_enabled(False)

    def _set_combo_by_data(self, combo: QComboBox, value: Any) -> None:
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def load_item(self, item: Item) -> None:
        self._item_id = item.id
        self._id_label.setText(str(item.id))
        self.title_edit.setText(item.title)
        self._set_combo_by_data(self.type_combo, MediaType(item.media_type))
        self._set_combo_by_data(self.status_combo, ItemStatus(item.status))
        self.rating_spin.setValue(0 if item.rating is None else int(item.rating))
        self.notes_edit.setPlainText(item.notes)
        self.cover_label.setPixmap(QPixmap())
        self.cover_label.setText("Loading cover…" if item.cover_id else "No cover")
        self.set_enabled(True)

    def current_item_id(self) -> int | None:
        return self._item_id

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

    def clear_cover(self) -> None:
        self.cover_label.setPixmap(QPixmap())
        self.cover_label.setText("No cover")

    def set_cover_path(self, path: Path | None) -> None:
        if path is None or not path.exists():
            self.clear_cover()
            return

        pix = QPixmap(str(path))
        if pix.isNull():
            self.clear_cover()
            return

        # Fit nicely in the label while keeping aspect
        pix = pix.scaled(
            self.cover_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.cover_label.setText("")
        self.cover_label.setPixmap(pix)
