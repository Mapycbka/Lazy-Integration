"""Оркестратор формирования конфигурационного файла."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from core.constants import (
    TRANSPORT_COLUMN_MAPPINGS,
    TRANSPORT_IP_TARGET_FIELDS,
    TRANSPORT_SHEET,
    TRANSPORT_SHEET_ALIASES,
    TRANSPORT_SOURCE_HEADER_ALIASES,
    TRANSPORT_TARGET_FIELDS,
)
from core.excel_loader import ExcelLoader
from core.rru_builder import RRUBuilder
from core.sector_builder import SectorBuilder
from core.template_writer import TemplateWriter
from core.validators import (
    TransportDataError,
    ValidationError,
    parse_ports,
    parse_slots,
    validate_user_input,
)
from models.app_state import UserInputState
from services.replace_service import ReplaceService
from utils.text_utils import extract_ipv4_address, extract_vlan_value, normalize_header


class MappingEngine:
    """Связывает GUI, чтение ДИ, построение сущностей и запись в шаблон."""

    def __init__(self, logger: Any) -> None:
        self.logger = logger
        self.excel_loader = ExcelLoader()
        self.sector_builder = SectorBuilder(logger)
        self.rru_builder = RRUBuilder(logger)
        self.template_writer = TemplateWriter(logger)
        self.replace_service = ReplaceService()

    def generate_file(
        self,
        state: UserInputState,
        port_dialog_callback: Callable[[list[tuple[str, int]], list[int]], dict[str, int] | None] | None = None,
        transport_issue_callback: Callable[[TransportDataError, dict[str, str]], dict[str, str] | None] | None = None,
    ) -> Path:
        """Формирует рабочую копию шаблона и возвращает путь к результату."""
        validate_user_input(state)
        state.slot_numbers = parse_slots(state.slot_numbers_raw)
        state.board_ports = parse_ports(state.board_ports_raw)

        di_workbook = self.excel_loader.open_di_workbook(state.di_path)
        template_workbook = self.excel_loader.open_template_workbook(state.template_path)
        template_workbook.close()
        di_sheet_names = self.excel_loader.resolve_di_sheet_names(di_workbook)
        self.logger.info(
            "Для ДИ использованы листы: 2G='%s', 4G='%s'",
            di_sheet_names["2G_BTS_Data"],
            di_sheet_names["4G_Data"],
        )
        gsm_rows = self.excel_loader.read_sheet_as_dicts(di_workbook, di_sheet_names["2G_BTS_Data"])
        lte_rows = self.excel_loader.read_sheet_as_dicts(di_workbook, di_sheet_names["4G_Data"])
        gsm_cells = self.sector_builder.build_gsm_records(gsm_rows)
        lte_cells = self.sector_builder.build_lte_records(lte_rows)
        ne_name = self.excel_loader.extract_ne_name(di_workbook)
        bsc_name = self.excel_loader.extract_bsc_name(di_workbook)
        if bsc_name:
            state.bsc_name = bsc_name
            self.logger.info("BSC NAME из ДИ: %s", bsc_name)
        transport_defaults = self._build_transport_defaults(lte_rows, ne_name, state.transport_port)

        if state.skip_ts_loading:
            transport_data = transport_defaults.copy()
            self.logger.info("Чтение ТС пропущено по выбору пользователя.")
        else:
            try:
                ts_workbook = self.excel_loader.open_ts_workbook(state.ts_path)
                ts_sheet_name = self.excel_loader.resolve_sheet_name(ts_workbook, TRANSPORT_SHEET_ALIASES)
                self.logger.info("Для ТС использован лист: %s", ts_sheet_name)
                ts_rows = self.excel_loader.read_sheet_as_dicts(
                    ts_workbook,
                    ts_sheet_name,
                    header_aliases=self._build_transport_header_candidates(),
                )
                transport_data = self._build_transport_data(ts_rows, transport_defaults)
            except ValidationError as error:
                transport_error = self._normalize_transport_error(error)
                self.logger.warning("Ошибка чтения ТС: %s", transport_error)
                if transport_issue_callback is None:
                    raise transport_error
                resolved_transport_data = transport_issue_callback(transport_error, transport_defaults.copy())
                if resolved_transport_data is None:
                    raise ValidationError("Формирование отменено пользователем на этапе обработки ТС.")
                transport_data = resolved_transport_data
                if not transport_data:
                    self.logger.warning(
                        "Пользователь пропустил заполнение ТС. DI-derived поля будут заполнены, "
                        "а транспортные поля останутся пустыми."
                    )
                else:
                    self.logger.info("Пользователь ввел ТС-параметры вручную.")

        chain_candidates = self.rru_builder.build_chain_candidates(gsm_cells, lte_cells, state)
        chain_head_bindings = self._resolve_head_ports(
            chain_candidates,
            state.slot_numbers,
            state.board_ports,
            port_dialog_callback,
        )

        bundle = self.rru_builder.build_bundle(gsm_cells, lte_cells, state, chain_head_bindings)
        if ne_name:
            bundle.ne_name = ne_name
        bundle.transport_data = transport_data
        bundle.transport_port = state.transport_port
        working_copy = self.template_writer.create_working_copy(state.template_path, bundle.ne_name or "result")
        if bundle.ne_name:
            try:
                replaced_names = self.replace_service.replace_ne_name(working_copy, bundle.ne_name, "NE Version")
                if replaced_names:
                    self.logger.info("NE Name заменен по шаблону: %s", ", ".join(replaced_names))
            except Exception as error:
                self.logger.warning("Не удалось выполнить глобальную замену NE Name по шаблону: %s", error)
        self._apply_optional_software_replacements(
            working_copy,
            state.bts_software,
            state.bsc_software,
        )
        result_path = self.template_writer.write_bundle(working_copy, bundle)
        self._apply_optional_software_replacements(
            result_path,
            state.bts_software,
            state.bsc_software,
        )
        self.template_writer._strip_external_refs(result_path)
        self.logger.info("Формирование завершено: %s", result_path)
        return result_path

    def save_result(self, source_path: str | Path, target_path: str | Path) -> Path:
        """Сохраняет готовый файл в выбранную пользователем папку."""
        return self.template_writer.save_result(source_path, target_path)

    def _resolve_head_ports(
        self,
        chain_candidates: list[tuple[str, int]],
        slot_numbers: list[int],
        board_ports: list[int],
        port_dialog_callback: Callable[
            [list[tuple[str, int]], list[int], list[int]],
            dict[str, tuple[int, int]] | None,
        ] | None,
    ) -> dict[str, tuple[int, int]]:
        if not chain_candidates:
            return {}
        if len(chain_candidates) == 1:
            rru, _ = chain_candidates[0]
            return {rru: (slot_numbers[0], board_ports[0])}

        if port_dialog_callback is None:
            return {
                rru: (
                    slot_numbers[index % len(slot_numbers)],
                    board_ports[index % len(board_ports)],
                )
                for index, (rru, _) in enumerate(chain_candidates)
            }

        selected = port_dialog_callback(chain_candidates, slot_numbers, board_ports)
        if selected is None:
            raise ValidationError("Формирование отменено пользователем на этапе выбора плат и портов RRUCHAIN.")
        return selected

    def _build_transport_defaults(
        self,
        lte_rows: list[dict[str, str]],
        ne_name: str,
        transport_port: str,
    ) -> dict[str, str]:
        """Готовит дефолтный набор полей транспортного листа."""
        transport_data = {field_name: "" for field_name in TRANSPORT_TARGET_FIELDS}

        enodeb_id = self.excel_loader.extract_first_non_empty_value(
            lte_rows,
            ("eNodeBID", "*eNodeB ID"),
        )
        if enodeb_id:
            transport_data["*eNodeB ID"] = enodeb_id

        digits = [part for part in __import__("re").findall(r"\d+", ne_name) if part]
        if digits:
            adjnode = digits[-1].lstrip("0") or "0"
            transport_data["ADJNODE (ID)"] = adjnode
            transport_data["SCTPLNK(BSC) (ID1)"] = f"{adjnode}0"

        transport_data["*Name"] = ne_name
        transport_data["*BTS Name"] = ne_name
        transport_data["*eNodeB Name"] = ne_name
        transport_data["Port"] = transport_port
        return transport_data

    def _build_transport_data(
        self,
        ts_rows: list[dict[str, str]],
        transport_defaults: dict[str, str],
    ) -> dict[str, str]:
        if not ts_rows:
            raise TransportDataError("Лист 'ip-план' в ТС пустой.")

        available_columns = set(ts_rows[0].keys())
        missing_columns = [
            source_column
            for source_column in TRANSPORT_COLUMN_MAPPINGS.keys()
            if self._resolve_transport_source_key(available_columns, source_column) is None
        ]
        if missing_columns:
            missing_str = ", ".join(missing_columns)
            raise TransportDataError(
                f"В листе 'ip-план' отсутствуют обязательные столбцы: {missing_str}",
                missing_columns=missing_columns,
            )

        transport_row: dict[str, str] = {}
        for row in ts_rows:
            if any(
                row.get(self._resolve_transport_source_key(row.keys(), source_column) or "", "").strip()
                for source_column in TRANSPORT_COLUMN_MAPPINGS.keys()
            ):
                transport_row = row
                break
        if not transport_row:
            raise TransportDataError("В листе 'ip-план' не найдено ни одной заполненной строки с ТС-параметрами.")

        transport_data = transport_defaults.copy()
        for source_column, target_column in TRANSPORT_COLUMN_MAPPINGS.items():
            source_key = self._resolve_transport_source_key(transport_row.keys(), source_column)
            raw_value = transport_row.get(source_key, "").strip() if source_key else ""
            if target_column in TRANSPORT_IP_TARGET_FIELDS:
                transport_data[target_column] = extract_ipv4_address(raw_value)
            elif target_column in {"OMCH Vlan", "ABIS Vlan", "S1 Vlan"}:
                transport_data[target_column] = extract_vlan_value(raw_value)
            else:
                transport_data[target_column] = raw_value
        return transport_data

    @staticmethod
    def _build_transport_header_candidates() -> tuple[str, ...]:
        """Формирует общий список допустимых заголовков ТС для поиска строки шапки."""
        candidates: list[str] = []
        for aliases in TRANSPORT_SOURCE_HEADER_ALIASES.values():
            candidates.extend(aliases)
        return tuple(dict.fromkeys(candidates))

    @staticmethod
    def _resolve_transport_source_key(
        available_headers: set[str] | list[str] | Any,
        logical_source_header: str,
    ) -> str | None:
        """Находит реальный заголовок ТС по списку алиасов."""
        normalized_lookup = {
            normalize_header(header): header
            for header in available_headers
            if str(header).strip()
        }
        aliases = TRANSPORT_SOURCE_HEADER_ALIASES.get(logical_source_header, (logical_source_header,))
        for alias in aliases:
            resolved = normalized_lookup.get(normalize_header(alias))
            if resolved:
                return resolved
        return None

    @staticmethod
    def _normalize_transport_error(error: ValidationError) -> TransportDataError:
        """Приводит ошибки чтения ТС к единому типу для GUI-сценария."""
        if isinstance(error, TransportDataError):
            return error

        message = str(error)
        if "не содержит заголовков" in message:
            return TransportDataError(
                "Лист ТС не содержит подходящих заголовков для чтения транспортных параметров."
            )
        return TransportDataError(message)

    def _apply_optional_software_replacements(
        self,
        working_copy: Path,
        bts_software: str,
        bsc_software: str,
    ) -> None:
        """Применяет опциональные замены версий ПО по всему шаблону."""
        if bts_software:
            replacements = self.replace_service.replace_bts_software(working_copy, bts_software)
            self.logger.info("Замена BTS выполнена, найдено совпадений: %s", replacements)

        if bsc_software:
            replacements = self.replace_service.replace_bsc_software(working_copy, bsc_software)
            self.logger.info("Замена BSC выполнена, найдено совпадений: %s", replacements)
