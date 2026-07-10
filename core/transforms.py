"""Функции преобразования бизнес-значений для заполнения шаблона."""

from __future__ import annotations

import re

from core.constants import BAND_TO_FREQUENCY_BAND, CHAIN_NO_RULES, CHAIN_NO_RULES_BY_REGION, TXRXMODE_TO_CHANNELS
from core.validators import ValidationError
from utils.text_utils import normalize_band, safe_string


def build_sector_equipment_id(
    source_type: str,
    chain_no: int | str,
    suffix: int = 0,
) -> str:
    """Формирует 5-значный Sector Equipment ID по типу источника и номеру цепочки."""
    source_prefix_map = {
        "2G": "2",
        "4G": "4",
    }
    prefix = source_prefix_map.get(source_type.upper())
    if prefix is None:
        raise ValidationError(f"Неизвестный тип источника для Sector Equipment ID: {source_type}")

    try:
        chain_value = int(str(chain_no).strip())
    except ValueError as error:
        raise ValidationError(f"Некорректное значение *Chain No. для Sector Equipment ID: {chain_no}") from error

    if suffix < 0 or suffix > 9:
        raise ValidationError(f"Некорректный суффикс Sector Equipment ID: {suffix}")

    return f"{prefix}{chain_value:03d}{suffix}"


def parse_band_to_frequency_band(raw_band: str) -> str:
    """Преобразует Band (HW) в код Frequency band."""
    normalized_band = normalize_band(raw_band)
    mapped = BAND_TO_FREQUENCY_BAND.get(normalized_band)
    if mapped is None:
        raise ValidationError(f"Неизвестное значение Band (HW): {raw_band}")
    return str(mapped)


def parse_bandwidth_to_cell_bw(raw_bandwidth: str) -> str:
    """Преобразует значение полосы в формат CELL_BW_NXX."""
    normalized = safe_string(raw_bandwidth).upper().replace(" ", "")
    match = re.search(r"(\d+)", normalized)
    if not match:
        raise ValidationError(f"Не удалось определить значение полосы: {raw_bandwidth}")

    multiplied = int(match.group(1)) * 5
    return f"CELL_BW_N{multiplied}"


def parse_txrxmode_to_channels(raw_mode: str) -> tuple[int, int]:
    """Возвращает число RX/TX каналов по TxRxmode."""
    normalized_mode = safe_string(raw_mode).upper()
    channels = TXRXMODE_TO_CHANNELS.get(normalized_mode)
    if channels is None:
        raise ValidationError(f"Неизвестное значение TxRxmode: {raw_mode}")
    return channels


def normalize_ports_input(value: str) -> list[int]:
    """Нормализует ввод портов из формы в отсортированный список целых значений."""
    text = safe_string(value)
    if not text:
        raise ValidationError("Поле портов платы пустое.")

    if re.fullmatch(r"\d+\s*-\s*\d+", text):
        start_text, end_text = re.split(r"\s*-\s*", text)
        start = int(start_text)
        end = int(end_text)
        if start > end:
            raise ValidationError("В диапазоне портов начало не может быть больше конца.")
        return list(range(start, end + 1))

    prepared = text.replace(",", " ")
    parts = [part for part in prepared.split() if part]
    if not parts:
        raise ValidationError("Не удалось разобрать значения портов.")

    if not all(part.isdigit() for part in parts):
        raise ValidationError(
            "Неверный формат поля с портами. Используйте, например: 0-2, 0 1 2 или 0,1,2."
        )

    # Сохраняем порядок, который ввел пользователь, и убираем дубликаты.
    normalized_ports: list[int] = []
    for part in parts:
        port = int(part)
        if port not in normalized_ports:
            normalized_ports.append(port)
    return normalized_ports


def resolve_rruchain_by_region_and_band(site_type: str, region: str, raw_band: str) -> int:
    """Определяет *Chain No. по типу площадки, региону и диапазону.

    Сначала проверяет региональные переопределения (CHAIN_NO_RULES_BY_REGION),
    затем — общие правила по типу площадки (CHAIN_NO_RULES).
    """
    normalized_band = normalize_band(raw_band)

    region_rules = CHAIN_NO_RULES_BY_REGION.get(site_type, {}).get(region)
    if region_rules is not None and normalized_band in region_rules:
        return region_rules[normalized_band]

    rules = CHAIN_NO_RULES.get(site_type)
    if rules is None:
        raise ValidationError(f"Неизвестный тип площадки: {site_type}")

    if normalized_band not in rules:
        raise ValidationError(
            f"Для региона '{region}' и типа площадки '{site_type}' не найдено правило для диапазона '{raw_band}'."
        )
    return rules[normalized_band]


def clone_template_rows(row_cloner, worksheet, source_row: int, copies_count: int) -> None:
    """Прокси-функция для универсального клонирования строк шаблона."""
    row_cloner.clone_row(worksheet, source_row, copies_count)


def gsm_freq_band_to_cell_type(freq_band: str) -> str:
    """Преобразует значение FREQ BAND (900/1800) из ДИ в тип GSM-ячейки."""
    normalized = freq_band.strip()
    if normalized == "900":
        return "GSM900"
    if normalized == "1800":
        return "DCS1800"
    return "GSM900"
