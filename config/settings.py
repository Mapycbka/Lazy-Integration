"""Общие настройки приложения и пути к рабочим каталогам."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOGS_DIR / "app.log"
TEMP_DIR = PROJECT_ROOT / "temp"

APP_TITLE = "Lazy Integration"
WINDOW_MIN_WIDTH = 980
WINDOW_MIN_HEIGHT = 760


def ensure_runtime_directories() -> None:
    """Создает каталоги, которые нужны приложению во время работы."""
    for directory in (TEMPLATES_DIR, LOGS_DIR, TEMP_DIR):
        directory.mkdir(parents=True, exist_ok=True)
