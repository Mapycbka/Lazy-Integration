"""Вспомогательные функции для чтения и записи Excel."""

from __future__ import annotations

from copy import copy
from typing import Iterable

from openpyxl.worksheet.worksheet import Worksheet

from utils.text_utils import normalize_header, safe_string


def build_header_index(
    worksheet: Worksheet,
    header_row: int,
) -> dict[str, int]:
    """Строит индекс заголовков по выбранной строке листа."""
    header_map: dict[str, int] = {}
    for column_index, cell in enumerate(worksheet[header_row], start=1):
        value = safe_string(cell.value)
        if value:
            header_map[value] = column_index
    return header_map


def find_best_header_row(
    worksheet: Worksheet,
    candidate_headers: Iterable[str],
    max_scan_rows: int,
) -> tuple[dict[str, int], int]:
    """Находит строку шапки, где найдено больше всего ожидаемых заголовков."""
    normalized_candidates = {normalize_header(header) for header in candidate_headers}
    best_map: dict[str, int] = {}
    best_row = 1
    best_score = -1

    for row_index in range(1, min(worksheet.max_row, max_scan_rows) + 1):
        current_map = build_header_index(worksheet, row_index)
        score = sum(
            1
            for header in current_map
            if normalize_header(header) in normalized_candidates
        )
        if score > best_score:
            best_score = score
            best_map = current_map
            best_row = row_index

    return best_map, best_row


def resolve_header_name(
    header_map: dict[str, int],
    aliases: Iterable[str],
) -> str | None:
    """Возвращает реальное имя заголовка с учетом алиасов."""
    normalized_lookup = {normalize_header(name): name for name in header_map}
    for alias in aliases:
        normalized_alias = normalize_header(alias)
        if normalized_alias in normalized_lookup:
            return normalized_lookup[normalized_alias]
    return None


def copy_cell_style(source_cell, target_cell) -> None:
    """Копирует форматирование и формулу ячейки."""
    target_cell._style = copy(source_cell._style)
    target_cell.font = copy(source_cell.font)
    target_cell.fill = copy(source_cell.fill)
    target_cell.border = copy(source_cell.border)
    target_cell.alignment = copy(source_cell.alignment)
    target_cell.number_format = copy(source_cell.number_format)
    target_cell.protection = copy(source_cell.protection)
    if source_cell.has_style:
        target_cell._style = copy(source_cell._style)
    if source_cell.hyperlink:
        target_cell._hyperlink = copy(source_cell.hyperlink)
    if source_cell.comment:
        target_cell.comment = copy(source_cell.comment)
