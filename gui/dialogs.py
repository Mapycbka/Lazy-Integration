"""Дополнительные диалоги приложения."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractButton,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from core.constants import TRANSPORT_TARGET_FIELDS
from core.validators import TransportDataError


class RRUChainPortDialog(QDialog):
    """Диалог выбора Head Slot/Port No. для RRU-цепочек."""

    def __init__(
        self,
        chain_candidates: list[tuple[str, int]],
        available_slots: list[int],
        available_ports: list[int],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Выбор плат и портов RRUCHAIN")
        self._slot_combos: dict[str, QComboBox] = {}
        self._port_combos: dict[str, QComboBox] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Для найденных RRU-цепочек выберите нужную плату и Head Port No. "
                "Эти значения будут записаны на лист RRUCHAIN(NODE)."
            )
        )

        form_layout = QFormLayout()
        for index, (rru, chain_no) in enumerate(chain_candidates):
            slot_combo = QComboBox()
            slot_combo.addItems([str(slot) for slot in available_slots])
            slot_combo.setCurrentIndex(index % len(available_slots))

            port_combo = QComboBox()
            port_combo.addItems([str(port) for port in available_ports])
            port_combo.setCurrentIndex(index % len(available_ports))

            compact_row = QWidget()
            compact_layout = QHBoxLayout(compact_row)
            compact_layout.setContentsMargins(0, 0, 0, 0)
            compact_layout.addWidget(QLabel("Плата:"))
            compact_layout.addWidget(slot_combo)
            compact_layout.addWidget(QLabel("Порт:"))
            compact_layout.addWidget(port_combo)
            compact_layout.addStretch(1)

            form_layout.addRow(f"RRU {rru} / Chain {chain_no}:", compact_row)
            self._slot_combos[rru] = slot_combo
            self._port_combos[rru] = port_combo

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_bindings(self) -> dict[str, tuple[int, int]]:
        """Возвращает выбор пользователя: плата и порт для каждой LTE-цепочки."""
        return {
            rru: (
                int(self._slot_combos[rru].currentText()),
                int(self._port_combos[rru].currentText()),
            )
            for rru in self._slot_combos
        }


class TransportIssueChoiceDialog(QMessageBox):
    """Диалог выбора действия при проблемах с ТС."""

    def __init__(self, error: TransportDataError, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Проблема с ТС-параметрами")
        self.setIcon(QMessageBox.Warning)
        self.setText(str(error))

        details: list[str] = []
        if error.missing_sheet:
            details.append(f"Отсутствует лист: {error.missing_sheet}")
        if error.missing_columns:
            details.append(f"Отсутствуют столбцы: {', '.join(error.missing_columns)}")
        if details:
            self.setInformativeText("\n".join(details))

        self.manual_button = self.addButton("Заполнить вручную", QMessageBox.AcceptRole)
        self.skip_button = self.addButton("Пропустить ТС", QMessageBox.DestructiveRole)
        self.cancel_button = self.addButton("Отмена", QMessageBox.RejectRole)


class TransportManualInputDialog(QDialog):
    """Диалог ручного ввода ТС-параметров для шаблона."""

    def __init__(self, initial_values: dict[str, str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Ручной ввод ТС-параметров")
        self._fields: dict[str, QLineEdit] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Введите значения для заполнения листа Base Station Transport Data. "
                "Если поле не нужно менять, оставьте текущее значение."
            )
        )

        form_layout = QFormLayout()
        for field_name in TRANSPORT_TARGET_FIELDS:
            line_edit = QLineEdit()
            line_edit.setText(initial_values.get(field_name, ""))
            form_layout.addRow(f"{field_name}:", line_edit)
            self._fields[field_name] = line_edit

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_transport_data(self) -> dict[str, str]:
        """Возвращает введенные пользователем ТС-параметры."""
        return {
            field_name: field.text().strip()
            for field_name, field in self._fields.items()
        }
