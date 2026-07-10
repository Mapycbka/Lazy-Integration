"""Преобразование текстовых значений и нормализация бизнес-полей."""

from __future__ import annotations

import re


def normalize_header(value: object) -> str:
    """Приводит заголовок к удобному виду для сравнения."""
    text = str(value or "").strip()
    return re.sub(r"\s+", " ", text).casefold()


def safe_string(value: object) -> str:
    """Безопасно превращает значение Excel в строку без None."""
    return str(value).strip() if value is not None else ""


def extract_ipv4_address(value: object) -> str:
    """Извлекает IPv4-адрес из строки.

    Нужен для ТС-параметров, где в ячейке может лежать адрес вместе с маской,
    комментарием или дополнительным текстом. Если IPv4 не найден, возвращаем
    исходное строковое значение, чтобы не потерять пользовательские данные.
    """
    text = safe_string(value)
    if not text:
        return ""

    match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
    if not match:
        return text
    return match.group(0)


def extract_vlan_value(value: object) -> str:
    """Извлекает чистое значение VLAN без пояснений в скобках и хвостов.

    Примеры:
    - ``3702 (vprn 71007000)`` -> ``3702``
    - ``3702(vprn 71007000)`` -> ``3702``
    - ``3702 / резерв`` -> ``3702``
    """
    text = safe_string(value)
    if not text:
        return ""

    text = re.split(r"\(", text, maxsplit=1)[0].strip()
    text = re.split(r"/", text, maxsplit=1)[0].strip()
    match = re.search(r"\d+", text)
    if match:
        return match.group(0)
    return text


def normalize_band(raw_band: str) -> str:
    """Нормализует значение диапазона к единому виду."""
    value = safe_string(raw_band).upper().replace("МГЦ", "").replace("MHZ", "")
    value = re.sub(r"\s+", " ", value).strip()
    replacements = {
        "BAND1": "2100",
        "BAND3": "1800",
        "BAND7": "2600",
        "BAND8": "900",
        "BAND20": "800",
        "BAND38": "2600 TDD",
        "2600TDD": "2600 TDD",
        "1800/2100": "1800/2100",
    }
    if value in replacements:
        return replacements[value]
    return value


def band_to_frequency_band(raw_band: str) -> str | None:
    """Преобразует диапазон в код поля Frequency band."""
    from core.transforms import parse_band_to_frequency_band

    try:
        return parse_band_to_frequency_band(raw_band)
    except Exception:
        return None


def bandwidth_to_cell_bw(raw_bandwidth: str) -> str | None:
    """Преобразует полосу в формат CELL_BW_NXX."""
    from core.transforms import parse_bandwidth_to_cell_bw

    try:
        return parse_bandwidth_to_cell_bw(raw_bandwidth)
    except Exception:
        return None


def txrxmode_to_channels(raw_mode: str) -> tuple[int, int] | None:
    """Возвращает количество RX/TX-каналов по TxRxmode."""
    from core.transforms import parse_txrxmode_to_channels

    try:
        return parse_txrxmode_to_channels(raw_mode)
    except Exception:
        return None


def padded_chain(chain_no: int) -> str:
    """Формирует среднюю часть идентификатора оборудования сектора."""
    return f"{chain_no:03d}"


def extract_antenna_number(ret_name: str) -> int | None:
    """Извлекает номер антенны из столбца RetName.

    Поддерживает форматы: a1, A1, а1, А1 (кириллица и латиница, без учёта регистра).
    Буква a/а должна быть в начале строки или после не-буквенного символа,
    чтобы не срабатывать на слова вроде «antenna1».

    Возвращает целое число (1, 2, 3…) или None, если паттерн не найден.
    """
    text = safe_string(ret_name)
    if not text:
        return None
    match = re.search(r"(?:^|[^a-zA-Zа-яА-Я])[aаAА](\d+)", text)
    if match:
        return int(match.group(1))
    return None


def compute_sector_order_by_antenna(antenna_numbers: list[int]) -> dict[int, int]:
    """Вычисляет порядковый номер сектора по списку номеров антенн.

    Правило: антенны сортируются по номеру, и порядковый сектор
    назначается по позиции в отсортированном уникальном ряду.

    Примеры:
        [1, 2, 3]       → {1: 1, 2: 2, 3: 3}
        [1, 3, 5]       → {1: 1, 3: 2, 5: 3}
        [2, 4, 6]       → {2: 1, 4: 2, 6: 3}
        [1, 1, 3, 3]    → {1: 1, 3: 2}
    """
    unique_sorted = sorted(set(antenna_numbers))
    return {antenna: order + 1 for order, antenna in enumerate(unique_sorted)}
