"""Переиспользуемые виджеты интерфейса."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)


class FilePickerRow(QWidget):
    """Строка интерфейса с кнопкой выбора файла и отображением пути."""

    def __init__(self, button_text: str, placeholder: str, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QPushButton(button_text)
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText(placeholder)

        layout.addWidget(self.button)
        layout.addWidget(self.path_edit, stretch=1)


class StatusBarWidget(QWidget):
    """Небольшой виджет для отображения статуса."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel("Статус: ожидание ввода")
        layout.addWidget(self.label)

    def set_status(self, text: str) -> None:
        self.label.setText(f"Статус: {text}")


class LogViewer(QTextEdit):
    """Поле журналирования операций."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Журнал выполнения появится здесь.")
