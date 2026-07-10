"""Настройка логирования в файл и интеграция логов с GUI."""

from __future__ import annotations

import logging
from typing import Callable

from config.settings import LOG_FILE, ensure_runtime_directories


def setup_logger(gui_callback: Callable[[str], None] | None = None) -> logging.Logger:
    """Создает общий logger приложения.

    Если передан gui_callback, каждое сообщение дополнительно уходит в окно логов.
    """
    ensure_runtime_directories()

    logger = logging.getLogger("bts_config_generator")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Не дублируем обработчики при повторном создании окна.
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if gui_callback is not None:
        logger.handlers = [
            handler for handler in logger.handlers if not isinstance(handler, GuiLogHandler)
        ]
        gui_handler = GuiLogHandler(gui_callback)
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)

    return logger


class GuiLogHandler(logging.Handler):
    """Легкий logging-handler, который отправляет сообщения в GUI."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self.callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            self.callback(message)
        except Exception:
            self.handleError(record)
