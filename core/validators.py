"""Валидация входных данных и бизнес-полей."""

from __future__ import annotations
from pathlib import Path

from core.constants import (
    DI_REQUIRED_SHEETS,
    REGIONS_BY_SITE_TYPE,
    SITE_TYPES,
    TEMPLATE_SHEETS,
    TRANSPORT_SHEET_ALIASES,
    TS_REQUIRED_SHEETS,
)
from models.app_state import UserInputState


class ValidationError(Exception):
    """Ошибки, которые можно безопасно показать пользователю."""


class TransportDataError(ValidationError):
    """Ошибки, связанные именно с чтением и переносом ТС-параметров."""

    def __init__(
        self,
        message: str,
        *,
        missing_sheet: str = "",
        missing_columns: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.missing_sheet = missing_sheet
        self.missing_columns = missing_columns or []


def validate_user_input(state: UserInputState) -> None:
    """Проверяет обязательные поля формы."""
    if not state.di_path:
        raise ValidationError("Файл ДИ не выбран.")
    if not state.template_path:
        raise ValidationError("Шаблон Excel не выбран.")
    if not state.template_name:
        raise ValidationError("Шаблон не выбран из списка.")
    if not state.skip_ts_loading and not state.ts_path:
        raise ValidationError("Файл ТС не выбран.")
    if not Path(state.di_path).exists():
        raise ValidationError(f"Файл ДИ не найден: {state.di_path}")
    if not state.skip_ts_loading and not Path(state.ts_path).exists():
        raise ValidationError(f"Файл ТС не найден: {state.ts_path}")
    if not Path(state.template_path).exists():
        raise ValidationError(f"Шаблон не найден: {state.template_path}")
    if state.site_type not in SITE_TYPES:
        raise ValidationError("Не выбран корректный тип площадки.")
    if state.region not in REGIONS_BY_SITE_TYPE.get(state.site_type, ()):
        raise ValidationError("Регион не соответствует выбранному типу площадки.")
    if not state.slot_numbers_raw.strip():
        raise ValidationError("Не указан номер платы/слота.")
    if not state.board_ports_raw.strip():
        raise ValidationError("Не указаны порты платы.")


def parse_ports(value: str) -> list[int]:
    """Нормализует ввод пользователя с портами платы."""
    from core.transforms import normalize_ports_input

    return normalize_ports_input(value)


def parse_slots(value: str) -> list[int]:
    """Нормализует ввод пользователя с номерами плат/слотов."""
    from core.transforms import normalize_ports_input

    return normalize_ports_input(value)


def validate_required_sheets(sheet_names: list[str], required_sheets: tuple[str, ...], context: str) -> None:
    """Проверяет наличие обязательных листов."""
    missing = [sheet for sheet in required_sheets if sheet not in sheet_names]
    if missing:
        missing_str = ", ".join(missing)
        raise ValidationError(f"В {context} отсутствуют обязательные листы: {missing_str}")


def validate_template_sheets(sheet_names: list[str]) -> None:
    """Проверяет обязательные листы шаблона."""
    validate_required_sheets(sheet_names, TEMPLATE_SHEETS, "шаблоне")


def validate_di_sheets(sheet_names: list[str]) -> None:
    """Проверяет обязательные листы ДИ."""
    validate_required_sheets(sheet_names, DI_REQUIRED_SHEETS, "файле ДИ")


def validate_ts_sheets(sheet_names: list[str]) -> None:
    """Проверяет обязательные листы ТС."""
    normalized_sheet_names = {_normalize_sheet_name(sheet_name) for sheet_name in sheet_names}
    normalized_aliases = {_normalize_sheet_name(alias) for alias in TRANSPORT_SHEET_ALIASES}
    if not normalized_sheet_names.intersection(normalized_aliases):
        raise TransportDataError(
            "В файле ТС отсутствует лист ip-план или его допустимый вариант написания.",
            missing_sheet=TS_REQUIRED_SHEETS[0],
        )


def _normalize_sheet_name(value: str) -> str:
    """Нормализует имя Excel-листа для сравнения вариантов написания."""
    normalized = value.casefold().strip()
    for symbol in (" ", "-", "_", "–", "—", ".", ","):
        normalized = normalized.replace(symbol, "")
    return normalized
