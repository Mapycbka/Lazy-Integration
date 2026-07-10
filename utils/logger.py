"""Настройка логирования в файл и окно приложения."""

from __future__ import annotations

import logging
from typing import Callable

from core.constants import LOG_FILE, LOGS_DIR, TEMP_DIR


class GuiLogHandler(logging.Handler):
    """Передает сообщения логгера в GUI-коллбек."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self.callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.callback(self.format(record))
        except Exception:
            self.handleError(record)


def setup_logger(gui_callback: Callable[[str], None] | None = None) -> logging.Logger:
    """Создает единый logger приложения."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("bs_config_app")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.handlers = [
        handler for handler in logger.handlers if not isinstance(handler, GuiLogHandler)
    ]
    if gui_callback is not None:
        gui_handler = GuiLogHandler(gui_callback)
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)

    return logger
