"""Построение GSM/LTE-сущностей из строк Excel."""

from __future__ import annotations

from typing import Any

from core.constants import GSM_REQUIRED_FIELDS, GSM_OPTIONAL_FIELDS, LTE_REQUIRED_FIELDS, LTE_OPTIONAL_FIELDS, OPTIONAL_COMMON_FIELDS
from core.transforms import parse_band_to_frequency_band, parse_bandwidth_to_cell_bw
from core.validators import ValidationError
from models.di_models import GSMCellRecord, LTECellRecord
from utils.text_utils import (
    normalize_band,
    safe_string,
)


class SectorBuilder:
    """Строит первичные сущности GSM/LTE из листов ДИ."""

    def __init__(self, logger: Any) -> None:
        self.logger = logger

    def build_gsm_records(self, rows: list[dict[str, str]]) -> list[GSMCellRecord]:
        """Строит список GSM-секторов."""
        records: list[GSMCellRecord] = []
        for index, row in enumerate(rows, start=2):
            try:
                ci = self._get_required_value(row, GSM_REQUIRED_FIELDS["ci"], "2G_BTS_Data", index)
                record = GSMCellRecord(
                    ci=ci,
                    cell_name=self._get_required_value(
                        row,
                        GSM_REQUIRED_FIELDS["cell_name"],
                        "2G_BTS_Data",
                        index,
                    ),
                    lac=self._get_required_value(row, GSM_REQUIRED_FIELDS["lac"], "2G_BTS_Data", index),
                    ncc=self._get_required_value(row, GSM_REQUIRED_FIELDS["ncc"], "2G_BTS_Data", index),
                    bcc=self._get_required_value(row, GSM_REQUIRED_FIELDS["bcc"], "2G_BTS_Data", index),
                    rac=self._get_required_value(row, GSM_REQUIRED_FIELDS["rac"], "2G_BTS_Data", index),
                    bcch_frequency=self._get_required_value(
                        row,
                        GSM_REQUIRED_FIELDS["bcch_frequency"],
                        "2G_BTS_Data",
                        index,
                    ),
                    power=self._get_required_value(row, GSM_REQUIRED_FIELDS["power"], "2G_BTS_Data", index),
                    trx_group_id=f"{ci}0",
                    rru=self._get_required_value(row, GSM_REQUIRED_FIELDS["rru"], "2G_BTS_Data", index),
                    band=self._get_optional_value(row, OPTIONAL_COMMON_FIELDS["band"]),
                    freq_band=self._get_optional_value(row, OPTIONAL_COMMON_FIELDS["gsm_freq_band"]),
                    txrx_mode=self._get_optional_value(row, OPTIONAL_COMMON_FIELDS["txrxmode"]),
                    ne_name=self._get_optional_value(row, OPTIONAL_COMMON_FIELDS["ne_name"]),
                    source_chain_no=self._get_optional_value(row, OPTIONAL_COMMON_FIELDS["chain_no"]),
                    ret_name=self._get_optional_value(row, GSM_OPTIONAL_FIELDS["ret_name"]),
                )
                records.append(record)
            except ValidationError as error:
                self.logger.warning(str(error))
        if not records:
            raise ValidationError("В листе '2G_BTS_Data' не найдено ни одной корректной GSM-записи.")
        return records

    def build_lte_records(self, rows: list[dict[str, str]]) -> list[LTECellRecord]:
        """Строит список LTE-секторов."""
        records: list[LTECellRecord] = []
        for index, row in enumerate(rows, start=2):
            try:
                raw_band = self._get_required_value(row, LTE_REQUIRED_FIELDS["band"], "4G_Data", index)
                frequency_band = parse_band_to_frequency_band(raw_band)

                raw_bandwidth = self._get_required_value(
                    row,
                    LTE_REQUIRED_FIELDS["bandwidth"],
                    "4G_Data",
                    index,
                )
                cell_bw = parse_bandwidth_to_cell_bw(raw_bandwidth)

                record = LTECellRecord(
                    local_cell_id=self._get_required_value(
                        row,
                        LTE_REQUIRED_FIELDS["local_cell_id"],
                        "4G_Data",
                        index,
                    ),
                    cell_name=self._get_required_value(
                        row,
                        LTE_REQUIRED_FIELDS["cell_name"],
                        "4G_Data",
                        index,
                    ),
                    tac=self._get_required_value(row, LTE_REQUIRED_FIELDS["tac"], "4G_Data", index),
                    band=normalize_band(raw_band),
                    frequency_band=frequency_band,
                    downlink_earfcn=self._get_required_value(
                        row,
                        LTE_REQUIRED_FIELDS["frequency"],
                        "4G_Data",
                        index,
                    ),
                    downlink_bandwidth=cell_bw,
                    uplink_bandwidth=cell_bw,
                    physical_cell_id=self._get_required_value(
                        row,
                        LTE_REQUIRED_FIELDS["pci"],
                        "4G_Data",
                        index,
                    ),
                    root_sequence_index=self._get_required_value(
                        row,
                        LTE_REQUIRED_FIELDS["root_sequence_index"],
                        "4G_Data",
                        index,
                    ),
                    reference_signal_power=self._get_required_value(
                        row,
                        LTE_REQUIRED_FIELDS["rsp"],
                        "4G_Data",
                        index,
                    ),
                    pb=self._get_required_value(row, LTE_REQUIRED_FIELDS["pb"], "4G_Data", index),
                    txrx_mode=self._get_required_value(
                        row,
                        LTE_REQUIRED_FIELDS["txrxmode"],
                        "4G_Data",
                        index,
                    ),
                    rru=self._get_required_value(row, LTE_REQUIRED_FIELDS["rru"], "4G_Data", index),
                    ne_name=self._get_optional_value(row, OPTIONAL_COMMON_FIELDS["ne_name"]),
                    source_chain_no=self._get_optional_value(row, OPTIONAL_COMMON_FIELDS["chain_no"]),
                    ret_name=self._get_optional_value(row, LTE_OPTIONAL_FIELDS["ret_name"]),
                )
                records.append(record)
            except ValidationError as error:
                self.logger.warning(str(error))
        if not records:
            raise ValidationError("В листе '4G_Data' не найдено ни одной корректной LTE-записи.")
        return records

    @staticmethod
    def _get_required_value(
        row: dict[str, str],
        aliases: tuple[str, ...],
        sheet_name: str,
        row_index: int,
    ) -> str:
        for alias in aliases:
            value = safe_string(row.get(alias))
            if value:
                return value
        alias_text = ", ".join(aliases)
        raise ValidationError(
            f"В листе '{sheet_name}' строка {row_index}: отсутствует обязательное поле ({alias_text})."
        )

    @staticmethod
    def _get_optional_value(row: dict[str, str], aliases: tuple[str, ...]) -> str:
        for alias in aliases:
            value = safe_string(row.get(alias))
            if value:
                return value
        return ""
