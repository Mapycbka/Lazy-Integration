"""Dataclass-модели внутренних сущностей, построенных из ДИ."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GSMCellRecord:
    ci: str
    cell_name: str
    lac: str
    ncc: str
    bcc: str
    rac: str
    bcch_frequency: str
    power: str
    trx_group_id: str
    rru: str
    band: str
    freq_band: str
    txrx_mode: str
    ne_name: str = ""
    source_chain_no: str = ""
    ret_name: str = ""
    chain_no: int | None = None
    sector_id: int | None = None
    sector_equipment_id: str = ""


@dataclass(slots=True)
class LTECellRecord:
    local_cell_id: str
    cell_name: str
    tac: str
    band: str
    frequency_band: str
    downlink_earfcn: str
    downlink_bandwidth: str
    uplink_bandwidth: str
    physical_cell_id: str
    root_sequence_index: str
    reference_signal_power: str
    pb: str
    txrx_mode: str
    rru: str
    ne_name: str = ""
    source_chain_no: str = ""
    ret_name: str = ""
    chain_no: int | None = None
    sector_id: int | None = None
    sector_equipment_id: str = ""


@dataclass(slots=True)
class RRUChainRecord:
    rru: str
    band: str
    chain_no: int
    head_slot_no: int
    head_port_no: int
    source_types: set[str] = field(default_factory=set)


@dataclass(slots=True)
class RRURecord:
    rru: str
    band: str
    chain_no: int
    subrack_no: int
    rru_name: str
    rx_channels: int
    tx_channels: int
    txrx_mode: str
    rf_working_mode: str = ""


@dataclass(slots=True)
class SectorRecord:
    rru: str
    sector_id: int
    sector_name: str
    sector_antenna: str


@dataclass(slots=True)
class SectorEquipmentRecord:
    sector_equipment_id: str
    sector_id: int
    sector_equipment_antenna: str
    source_type: str
    txrx_mode: str
    rru: str


@dataclass(slots=True)
class ProcessedDataBundle:
    """Полный набор промежуточных данных для записи в шаблон."""

    ne_name: str
    gsm_cells: list[GSMCellRecord]
    lte_cells: list[LTECellRecord]
    rru_chains: list[RRUChainRecord]
    rrus: list[RRURecord]
    sectors: list[SectorRecord]
    sector_equipments: list[SectorEquipmentRecord]
    slot_numbers: list[int]
    board_ports: list[int]
    transport_data: dict[str, str] = field(default_factory=dict)
    transport_port: str = ""
