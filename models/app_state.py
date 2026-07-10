"""Модели состояния приложения и пользовательского ввода."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class UserInputState:
    """Текущее состояние формы, введенное пользователем."""

    di_path: str = ""
    ts_path: str = ""
    skip_ts_loading: bool = False
    template_path: str = ""
    template_name: str = ""
    site_type: str = ""
    region: str = ""
    bbu_type: str = "3900"
    bts_software: str = ""
    bsc_software: str = ""
    slot_numbers_raw: str = ""
    board_ports_raw: str = ""
    transport_port: str = "0"
    bsc_name: str = ""
    slot_numbers: list[int] = field(default_factory=list)
    board_ports: list[int] = field(default_factory=list)


@dataclass(slots=True)
class GenerationArtifacts:
    """Служебные пути, которые появляются в процессе генерации."""

    working_copy_path: Path | None = None
    saved_result_path: Path | None = None
