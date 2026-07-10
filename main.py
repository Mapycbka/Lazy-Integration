"""Точка входа в desktop-приложение формирования конфигурации БС."""

from __future__ import annotations

import sys

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> int:
    """Создает QApplication и запускает главное окно."""
    app = QApplication(sys.argv)
    app.setApplicationName("Lazy Integration")

    # appUserModelID нужен для корректного отображения иконки на панели задач Windows
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("LazyIntegration")

    icon_path = Path(__file__).parent / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
