"""Настройки заполнения листов шаблона."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SheetWriteConfig:
    """Конфигурация одного листа шаблона."""

    sheet_name: str
    data_start_row: int = 2
    header_scan_rows: int = 8
    clone_from_row: int | None = None
    single_record_only: bool = False
