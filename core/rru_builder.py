"""Построение RRU-цепочек, RRU, секторов и оборудования сектора."""

from __future__ import annotations

from collections import defaultdict
import re
from typing import Any

from core.transforms import (
    build_sector_equipment_id,
    parse_txrxmode_to_channels,
    resolve_rruchain_by_region_and_band,
)
from core.validators import ValidationError
from models.app_state import UserInputState
from models.di_models import (
    GSMCellRecord,
    LTECellRecord,
    ProcessedDataBundle,
    RRUChainRecord,
    RRURecord,
    SectorEquipmentRecord,
    SectorRecord,
)
from utils.text_utils import normalize_band, extract_antenna_number, compute_sector_order_by_antenna
from core.constants import BAND_TO_RF_WORKING_MODE


class RRUBuilder:
    """Строит связанные сущности на основе GSM/LTE-записей и настроек пользователя."""

    SHARED_2T2R_PORT_PATTERNS = (
        ("R0A", "R0B"),
        ("R0A", "R0C"),
        ("R0B", "R0D"),
        ("R0C", "R0D"),
    )

    def __init__(self, logger: Any) -> None:
        self.logger = logger

    def build_bundle(
        self,
        gsm_cells: list[GSMCellRecord],
        lte_cells: list[LTECellRecord],
        state: UserInputState,
        head_bindings: dict[str, tuple[int, int]],
    ) -> ProcessedDataBundle:
        """Создает полный пакет промежуточных сущностей."""
        rru_profiles = self._build_rru_profiles(gsm_cells, lte_cells, state.site_type)
        chain_map = self._assign_chain_numbers(rru_profiles, state.site_type, state.region)
        self._enrich_rru_chain_numbers(gsm_cells, lte_cells, chain_map)

        sector_profiles = self._build_sector_profiles(
            gsm_cells,
            lte_cells,
            rru_profiles,
            state.site_type,
            state.region,
        )
        self._enrich_sector_entities(gsm_cells, lte_cells, sector_profiles, rru_profiles, chain_map)

        rru_chains = self._build_rru_chains(
            rru_profiles,
            chain_map,
            state.slot_numbers,
            head_bindings,
            state.board_ports,
        )
        rrus = self._build_rru_records(rru_profiles, chain_map)
        sectors = self._build_sector_records(sector_profiles, chain_map)
        sector_equipments = self._build_sector_equipment_records(
            gsm_cells,
            lte_cells,
            sector_profiles,
            rru_profiles,
            chain_map,
        )
        ne_name = self._pick_ne_name(gsm_cells, lte_cells)

        return ProcessedDataBundle(
            ne_name=ne_name,
            gsm_cells=gsm_cells,
            lte_cells=lte_cells,
            rru_chains=rru_chains,
            rrus=rrus,
            sectors=sectors,
            sector_equipments=sector_equipments,
            slot_numbers=state.slot_numbers,
            board_ports=state.board_ports,
        )

    def build_chain_candidates(
        self,
        gsm_cells: list[GSMCellRecord],
        lte_cells: list[LTECellRecord],
        state: UserInputState,
    ) -> list[tuple[str, int]]:
        """Возвращает всех кандидатов для выбора Head Slot/Port No. по RRU-цепочкам.

        Включает все уникальные РРЮ (2G-only, 4G-only и shared),
        чтобы пользователь мог задать плату и порт для каждой цепочки.
        """
        profiles = self._build_rru_profiles(gsm_cells, lte_cells, state.site_type)
        chain_map = self._assign_chain_numbers(profiles, state.site_type, state.region)

        candidates: list[tuple[str, int]] = []
        for rru, profile in profiles.items():
            candidates.append((rru, chain_map[rru]))
        candidates.sort(key=lambda item: item[1])
        return candidates

    def _build_rru_profiles(
        self,
        gsm_cells: list[GSMCellRecord],
        lte_cells: list[LTECellRecord],
        site_type: str,
    ) -> dict[str, dict[str, Any]]:
        profiles: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "bands": set(),
                "source_types": set(),
                "lte_modes": [],
                "antenna_number": None,
            }
        )

        for record in gsm_cells:
            profile = profiles[record.rru]
            band = normalize_band(record.band)
            if not band:
                band = normalize_band(record.freq_band)
            if band:
                profile["bands"].add(band)
            profile["source_types"].add("2G")
            # Извлекаем номер антенны из RetName; берём минимальный,
            # если на одном RRU несколько записей с разными антеннами.
            antenna_num = extract_antenna_number(record.ret_name)
            if antenna_num is not None:
                if profile["antenna_number"] is None or antenna_num < profile["antenna_number"]:
                    profile["antenna_number"] = antenna_num

        for record in lte_cells:
            profile = profiles[record.rru]
            profile["bands"].add(normalize_band(record.band))
            profile["source_types"].add("4G")
            profile["lte_modes"].append(record.txrx_mode)
            # Извлекаем номер антенны из RetName; берём минимальный.
            antenna_num = extract_antenna_number(record.ret_name)
            if antenna_num is not None:
                if profile["antenna_number"] is None or antenna_num < profile["antenna_number"]:
                    profile["antenna_number"] = antenna_num

        for rru, profile in profiles.items():
            profile["resolved_band"] = self._resolve_rru_band(profile["bands"], site_type, rru)
            profile["dominant_txrx"] = self._resolve_txrx_mode(profile["lte_modes"], rru)
            profile["effective_txrx"] = self._resolve_effective_rru_txrx(profile)

        return profiles

    def _assign_chain_numbers(
        self,
        profiles: dict[str, dict[str, Any]],
        site_type: str,
        region: str,
    ) -> dict[str, int]:
        """Назначает *Chain No. только по уникальным RRU из ДИ.

        RRU сортируются по номеру антенны (RetName), чтобы chain_no
        совпадал с порядком секторов: RRU с A1 получает наименьший
        chain_no в группе, A2 — следующий и т.д.
        """
        chain_map: dict[str, int] = {}
        chain_offsets: dict[int, int] = defaultdict(int)

        # Сортируем RRU по номеру антенны внутри каждой band_group,
        # чтобы chain_no соответствовал порядку секторов.
        sorted_profiles = sorted(
            profiles.items(),
            key=lambda item: (item[1].get("antenna_number") or 999),
        )

        for rru, profile in sorted_profiles:
            base_chain_no = resolve_rruchain_by_region_and_band(
                site_type,
                region,
                profile["resolved_band"],
            )
            chain_map[rru] = base_chain_no + chain_offsets[base_chain_no]
            chain_offsets[base_chain_no] += 1
        return chain_map

    def _enrich_rru_chain_numbers(
        self,
        gsm_cells: list[GSMCellRecord],
        lte_cells: list[LTECellRecord],
        chain_map: dict[str, int],
    ) -> None:
        """Записывает в записи ДИ физический RRU chain_no."""
        for record in gsm_cells:
            record.chain_no = chain_map[record.rru]

        for record in lte_cells:
            record.chain_no = chain_map[record.rru]

    def _build_sector_profiles(
        self,
        gsm_cells: list[GSMCellRecord],
        lte_cells: list[LTECellRecord],
        rru_profiles: dict[str, dict[str, Any]],
        site_type: str,
        region: str,
    ) -> dict[tuple[str, str], dict[str, Any]]:
        """Строит физические сектора.

        Секторы считаются отдельно от RRU. Если в 2G и 4G совпадают имя RRU и
        номер сектора из имени ячейки, мы считаем это одним физическим сектором.
        """
        sector_profiles: dict[tuple[str, str], dict[str, Any]] = {}
        ordered_keys: list[tuple[str, str]] = []

        for record in [*gsm_cells, *lte_cells]:
            band_group, marker = self._build_sector_key(record, rru_profiles)
            key = (band_group, marker)

            if key not in sector_profiles:
                sector_profiles[key] = {
                    "band_group": band_group,
                    "display_band": self._resolve_sector_display_band(record, band_group),
                    "marker": marker,
                    "source_types": set(),
                    "rrus": set(),
                    "rru_list": [],          # ordered unique RRU names
                    "lte_modes": [],
                    "records": [],
                    "sector_id": 0,
                    "antenna_reference_id": 0,
                    "sector_name": "",
                    "sector_ports": (),
                    "shared_2t2r_split": False,
                }
                ordered_keys.append(key)

            profile = sector_profiles[key]
            profile["source_types"].add("4G" if isinstance(record, LTECellRecord) else "2G")
            if record.rru not in profile["rrus"]:
                profile["rrus"].add(record.rru)
                profile["rru_list"].append(record.rru)
            if isinstance(record, LTECellRecord):
                profile["lte_modes"].append(record.txrx_mode)
            profile["records"].append(record)

        # Считаем кандидатов на shared split по RRU: сектор с 2G+4G и 2T2R
        rru_shared_candidates: dict[str, int] = defaultdict(int)
        for profile in sector_profiles.values():
            if self._is_shared_2t2r_candidate(profile):
                for rru in profile["rrus"]:
                    rru_shared_candidates[rru] += 1

        # Форсируем 4T4R только для RRU, которые реально делят несколько 2T2R секторов
        for rru, count in rru_shared_candidates.items():
            if count >= 2:
                rru_profiles[rru]["effective_txrx"] = "4T4R"

        # Группируем сектора по base_sector_id (а не по band_group),
        # чтобы разные band-группы с одинаковым base_chain_no
        # (например "1800/2100" и "1800/2100/2600" → base 200)
        # получали непересекающиеся sector_id.
        keys_by_base: dict[int, list[tuple[str, str]]] = defaultdict(list)
        for key in ordered_keys:
            band_group = key[0]
            base = resolve_rruchain_by_region_and_band(site_type, region, band_group)
            keys_by_base[base].append(key)

        for base_sector_id, base_keys in keys_by_base.items():
            shared_split_keys = [
                key for key in base_keys if self._is_shared_2t2r_sector(sector_profiles[key], rru_profiles)
            ]

            # Вычисляем порядковый номер сектора по номерам антенн.
            # Маркер «a3» → antenna_number=3; цифровой маркер «3» → antenna_number=3.
            antenna_numbers = []
            for key in base_keys:
                profile = sector_profiles[key]
                marker = profile["marker"]
                if marker.startswith("a"):
                    try:
                        antenna_numbers.append(int(marker[1:]))
                    except ValueError:
                        antenna_numbers.append(0)
                else:
                    # Маркер из cell_name может быть числом ("1", "2", "3")
                    try:
                        antenna_numbers.append(int(marker))
                    except ValueError:
                        antenna_numbers.append(0)

            sector_order_map = compute_sector_order_by_antenna(antenna_numbers)

            # Shared split всегда начинается с PATTERN[1] (R0A,R0C),
            # т.к. PATTERN[0] (R0A,R0B) зарезервирован для standalone 2T2R
            pattern_offset = 1

            for key_index, key in enumerate(base_keys):
                profile = sector_profiles[key]
                antenna_num = antenna_numbers[key_index]
                sector_order = sector_order_map.get(antenna_num, key_index + 1)
                profile["sector_id"] = base_sector_id + sector_order - 1
                profile["antenna_reference_id"] = profile["sector_id"]
                profile["sector_name"] = f"{profile['display_band']}_{sector_order - 1}"

                if key in shared_split_keys:
                    split_index = shared_split_keys.index(key)
                    first_shared = sector_profiles[shared_split_keys[0]]
                    if split_index > 0:
                        profile["antenna_reference_id"] = first_shared["sector_id"]
                    profile["shared_2t2r_split"] = True
                    profile["split_index"] = split_index
                    profile["sector_ports"] = self.SHARED_2T2R_PORT_PATTERNS[
                        (split_index + pattern_offset) % len(self.SHARED_2T2R_PORT_PATTERNS)
                    ]
                else:
                    sector_mode = self._resolve_sector_txrx(profile)
                    profile["sector_ports"] = self._default_ports_for_txrx(sector_mode)

        return sector_profiles

    def _enrich_sector_entities(
        self,
        gsm_cells: list[GSMCellRecord],
        lte_cells: list[LTECellRecord],
        sector_profiles: dict[tuple[str, str], dict[str, Any]],
        rru_profiles: dict[str, dict[str, Any]],
        chain_map: dict[str, int],
    ) -> None:
        """Записывает sector_id и sector equipment id обратно в записи ДИ.

        Sector Equipment ID формируется из chain_no конкретного RRU записи,
        т.к. chain_no уникален для каждого RRU. sector_id записи —
        базовый sector_id сектора (один на все RRU сектора).
        Для shared-split секторов split_index добавляется к суффиксу,
        чтобы разные подсекторы на одном RRU получили разные SE ID.
        """
        for record in gsm_cells:
            key = self._build_sector_key(record, rru_profiles)
            profile = sector_profiles[key]
            sector_id = profile["sector_id"]
            record.sector_id = sector_id
            chain_no = chain_map.get(record.rru, 0)
            split_suffix = profile.get("split_index", 0)
            record.sector_equipment_id = build_sector_equipment_id("2G", chain_no, split_suffix)

        for record in lte_cells:
            key = self._build_sector_key(record, rru_profiles)
            profile = sector_profiles[key]
            sector_id = profile["sector_id"]
            record.sector_id = sector_id
            chain_no = chain_map.get(record.rru, 0)
            band_suffix = self._resolve_lte_sector_equipment_suffix(record, rru_profiles)
            split_suffix = profile.get("split_index", 0)
            record.sector_equipment_id = build_sector_equipment_id(
                "4G",
                chain_no,
                split_suffix + band_suffix,
            )

    def _build_rru_chains(
        self,
        profiles: dict[str, dict[str, Any]],
        chain_map: dict[str, int],
        slot_numbers: list[int],
        head_bindings: dict[str, tuple[int, int]],
        board_ports: list[int],
    ) -> list[RRUChainRecord]:
        records: list[RRUChainRecord] = []
        default_slot = slot_numbers[0]
        default_port = board_ports[0]

        for rru, chain_no in sorted(chain_map.items(), key=lambda item: item[1]):
            head_slot, head_port = head_bindings.get(rru, (default_slot, default_port))
            records.append(
                RRUChainRecord(
                    rru=rru,
                    band=profiles[rru]["resolved_band"],
                    chain_no=chain_no,
                    head_slot_no=head_slot,
                    head_port_no=head_port,
                    source_types=set(profiles[rru]["source_types"]),
                )
            )
        return records

    def _build_rru_records(
        self,
        profiles: dict[str, dict[str, Any]],
        chain_map: dict[str, int],
    ) -> list[RRURecord]:
        """Строит одну строку RRU(NODE) на каждый уникальный RRU из ДИ."""
        band_counters: dict[str, int] = defaultdict(int)
        records: list[RRURecord] = []

        for rru, chain_no in sorted(chain_map.items(), key=lambda item: item[1]):
            band = profiles[rru]["resolved_band"]
            txrx_mode = profiles[rru]["effective_txrx"]
            try:
                channels = parse_txrxmode_to_channels(txrx_mode)
            except ValidationError:
                self.logger.warning(
                    "Неизвестный TxRxmode для RRU '%s': %s. Используется 2T2R по умолчанию.",
                    rru,
                    txrx_mode,
                )
                channels = (2, 2)

            rf_working_mode = BAND_TO_RF_WORKING_MODE.get(band, "")
            if not rf_working_mode:
                self.logger.warning(
                    "Неизвестный RF Unit Working Mode для RRU '%s' с диапазоном '%s'.",
                    rru,
                    band,
                )

            index = band_counters[band]
            band_counters[band] += 1
            records.append(
                RRURecord(
                    rru=rru,
                    band=band,
                    chain_no=chain_no,
                    subrack_no=chain_no,
                    rru_name=f"{band}_{index}",
                    rx_channels=channels[0],
                    tx_channels=channels[1],
                    txrx_mode=txrx_mode,
                    rf_working_mode=rf_working_mode,
                )
            )
        return records

    def _build_sector_records(
        self,
        sector_profiles: dict[tuple[str, str], dict[str, Any]],
        chain_map: dict[str, int],
    ) -> list[SectorRecord]:
        """Строит записи SECTOR(NODE): одну строку на каждый RRU в секторе.

        Все строки одного сектора имеют одинаковый *Sector ID,
        но каждая ссылается на свой RRU (по chain_no/subrack_no).
        """
        records: list[SectorRecord] = []

        for profile in sorted(sector_profiles.values(), key=lambda item: item["sector_id"]):
            sector_id = profile["sector_id"]
            sector_ports = profile["sector_ports"]
            for rru in profile["rru_list"]:
                chain_no = chain_map.get(rru, 0)
                records.append(
                    SectorRecord(
                        rru=rru,
                        sector_id=sector_id,
                        sector_name=profile["sector_name"],
                        sector_antenna=self._format_sector_antenna(
                            chain_no,
                            sector_ports,
                        ),
                    )
                )

        return records

    def _build_sector_equipment_records(
        self,
        gsm_cells: list[GSMCellRecord],
        lte_cells: list[LTECellRecord],
        sector_profiles: dict[tuple[str, str], dict[str, Any]],
        rru_profiles: dict[str, dict[str, Any]],
        chain_map: dict[str, int],
    ) -> list[SectorEquipmentRecord]:
        """Строит записи SECTOREQM: одну на уникальный Sector Equipment ID.

        Каждая запись получает уникальный Sector Equipment ID на основе chain_no RRU.
        На multi-band RRU (1800/2100) каждый диапазон получает свой ID (суффикс 0/1),
        поэтому для LTE дедупликация идёт по (sector_equipment_id),
        а не по (sector_id, rru, source_type), чтобы не терять второй диапазон.
        *Sector ID — базовый sector_id сектора (один на все RRU сектора).
        Sector Equipment Antenna ссылается на chain_no (subrack_no) конкретного RRU.
        """
        seen_ids: set[str] = set()  # sector_equipment_id (уникален глобально)
        records: list[SectorEquipmentRecord] = []

        for record in gsm_cells:
            sector_equip_id = record.sector_equipment_id
            if sector_equip_id in seen_ids:
                continue
            seen_ids.add(sector_equip_id)
            key = self._build_sector_key(record, rru_profiles)
            profile = sector_profiles[key]
            sector_id = int(record.sector_id or 0)
            chain_no = chain_map.get(record.rru, 0)
            records.append(
                SectorEquipmentRecord(
                    sector_equipment_id=sector_equip_id,
                    sector_id=sector_id,
                    sector_equipment_antenna=self._format_sector_equipment_antenna(
                        chain_no,
                        self._resolve_equipment_ports("2G", profile, rru_profiles[record.rru]),
                    ),
                    source_type="2G",
                    txrx_mode="2T2R",
                    rru=record.rru,
                )
            )

        for record in lte_cells:
            sector_equip_id = record.sector_equipment_id
            if sector_equip_id in seen_ids:
                continue
            seen_ids.add(sector_equip_id)
            key = self._build_sector_key(record, rru_profiles)
            profile = sector_profiles[key]
            sector_id = int(record.sector_id or 0)
            chain_no = chain_map.get(record.rru, 0)
            records.append(
                SectorEquipmentRecord(
                    sector_equipment_id=sector_equip_id,
                    sector_id=sector_id,
                    sector_equipment_antenna=self._format_sector_equipment_antenna(
                        chain_no,
                        self._resolve_equipment_ports("4G", profile, rru_profiles[record.rru]),
                    ),
                    source_type="4G",
                    txrx_mode=record.txrx_mode,
                    rru=record.rru,
                )
            )

        return records

    @staticmethod
    def _resolve_lte_sector_equipment_suffix(
        record: LTECellRecord,
        rru_profiles: dict[str, dict[str, Any]],
    ) -> int:
        """Возвращает последнюю цифру Sector Equipment ID для LTE.

        На multi-band RRU (1800/2100) диапазону 1800 присваивается суффикс 0,
        а диапазону 2100 — суффикс 1. Для RRU с единственным диапазоном
        суффикс всегда 0.
        """
        resolved_band = rru_profiles.get(record.rru, {}).get("resolved_band", "")
        if resolved_band in ("1800/2100", "1800/2100/2600"):
            record_band = normalize_band(record.band)
            if record_band == "2100":
                return 1
            return 0
        return 0

    @staticmethod
    def _extract_band_from_rru_name(rru: str) -> str:
        """Определяет диапазон по номеру модели RRU.

        Из имени вида 'RRU_4 - RRU5909 for Multi-mode 1800MHz'
        извлекается только модель 'RRU5909', а диапазон берётся из справочника
        RRU_MODEL_TO_BAND. Текст описания после номера модели игнорируется,
        т.к. может не соответствовать реальному диапазону.
        """
        from core.constants import RRU_MODEL_TO_BAND

        match = re.search(r"(RRU\d{4})", rru, re.IGNORECASE)
        if match:
            model = match.group(1).upper()
            band = RRU_MODEL_TO_BAND.get(model, "")
            if band:
                return band
        return ""

    def _resolve_rru_band(self, bands: set[str], site_type: str, rru: str) -> str:
        normalized_bands = {normalize_band(band) for band in bands if normalize_band(band)}
        if not normalized_bands:
            fallback = self._extract_band_from_rru_name(rru)
            if fallback:
                self.logger.info(
                    "Диапазон для RRU '%s' определён из названия: '%s'.",
                    rru,
                    fallback,
                )
                normalized_bands.add(fallback)
        if not normalized_bands:
            raise ValidationError(f"Для RRU '{rru}' не удалось определить диапазон.")

        if normalized_bands == {"1800", "2100"}:
            return "1800/2100"
        if normalized_bands == {"1800", "2100", "2600"}:
            return "1800/2100/2600"

        if len(normalized_bands) == 1:
            return next(iter(normalized_bands))

        preferred_order = ["1800/2100", "2600 TDD", "2600", "2100", "1800", "900", "800"]
        for band in preferred_order:
            if band in normalized_bands:
                self.logger.warning(
                    "Для RRU '%s' найдено несколько диапазонов %s. Использован '%s'.",
                    rru,
                    sorted(normalized_bands),
                    band,
                )
                return band

        fallback_band = sorted(normalized_bands)[0]
        self.logger.warning(
            "Для RRU '%s' используется резервный диапазон '%s' для типа площадки '%s'.",
            rru,
            fallback_band,
            site_type,
        )
        return fallback_band

    @staticmethod
    def _resolve_effective_rru_txrx(profile: dict[str, Any]) -> str:
        """Определяет TxRx для RRU(NODE).

        Без форсирования 4T4R — решение о shared split принимается
        в _build_sector_profiles, где видно, сколько секторов сидит на RRU.
        """
        return profile.get("dominant_txrx") or "2T2R"

    def _resolve_sector_band_group(
        self,
        record: GSMCellRecord | LTECellRecord,
        rru_profiles: dict[str, dict[str, Any]],
    ) -> str:
        profile_band = rru_profiles[record.rru]["resolved_band"]
        # Любой мульти-band RRU (содержит "/") группируется как единый сектор
        if "/" in profile_band:
            return profile_band
        return normalize_band(record.band) or profile_band

    def _resolve_sector_display_band(
        self,
        record: GSMCellRecord | LTECellRecord,
        band_group: str,
    ) -> str:
        record_band = normalize_band(record.band)
        return record_band or band_group

    def _resolve_txrx_mode(self, lte_modes: list[str], rru: str) -> str:
        if not lte_modes:
            return "2T2R"
        normalized_modes = [mode.strip().upper() for mode in lte_modes if mode.strip()]
        if not normalized_modes:
            return "2T2R"
        if "4T4R" in normalized_modes:
            return "4T4R"
        if "2T2R" in normalized_modes:
            return "2T2R"
        self.logger.warning("Для RRU '%s' найден неизвестный TxRxmode: %s", rru, normalized_modes[0])
        return normalized_modes[0]

    def _resolve_sector_txrx(self, profile: dict[str, Any]) -> str:
        if not profile["lte_modes"]:
            return "2T2R"
        normalized_modes = [mode.strip().upper() for mode in profile["lte_modes"] if mode.strip()]
        if "4T4R" in normalized_modes:
            return "4T4R"
        return "2T2R"

    @staticmethod
    def _is_shared_2t2r_candidate(sector_profile: dict[str, Any]) -> bool:
        """Проверяет, может ли сектор участвовать в shared split, без учёта effective_txrx RRU."""
        if sector_profile["source_types"] != {"2G", "4G"}:
            return False
        normalized_modes = [
            mode.strip().upper() for mode in sector_profile.get("lte_modes", []) if mode.strip()
        ]
        if "4T4R" in normalized_modes:
            return False
        return True

    def _is_shared_2t2r_sector(
        self,
        sector_profile: dict[str, Any],
        rru_profiles: dict[str, dict[str, Any]],
    ) -> bool:
        if sector_profile["source_types"] != {"2G", "4G"}:
            return False
        if self._resolve_sector_txrx(sector_profile) != "2T2R":
            return False

        for rru in sector_profile["rrus"]:
            rru_profile = rru_profiles.get(rru, {})
            if rru_profile.get("source_types") == {"2G", "4G"} and rru_profile.get("effective_txrx") == "4T4R":
                return True
        return False

    @staticmethod
    def _resolve_equipment_ports(
        source_type: str,
        sector_profile: dict[str, Any],
        rru_profile: dict[str, Any],
    ) -> tuple[str, ...]:
        """Определяет порты для Sector Equipment Antenna.

        Для 2G на общем 4T4R-RRU используем 2T2R-поднабор портов.
        Если это сценарий распределения нескольких 2T2R-секторов по общему RRU,
        используем уже вычисленный split-паттерн.
        """
        if source_type == "2G":
            if sector_profile.get("shared_2t2r_split"):
                return sector_profile["sector_ports"]
            if rru_profile.get("source_types") == {"2G", "4G"} and rru_profile.get("effective_txrx") == "4T4R":
                return ("R0A", "R0C")
        return sector_profile["sector_ports"]

    @staticmethod
    def _default_ports_for_txrx(txrx_mode: str) -> tuple[str, ...]:
        if txrx_mode == "4T4R":
            return ("R0A", "R0B", "R0C", "R0D")
        return ("R0A", "R0B")

    @staticmethod
    def _format_sector_antenna(sector_id: int, ports: tuple[str, ...]) -> str:
        return ";".join(f"0,{sector_id},0,{port}" for port in ports)

    @staticmethod
    def _format_sector_antenna_multi_rru(
        rru_list: list[str],
        ports: tuple[str, ...],
        chain_map: dict[str, int],
    ) -> str:
        """Формирует Sector Antenna для сектора с несколькими RRU.

        Каждый RRU в секторе перечисляется со своим chain_no (subrack_no)
        и набором портов. Формат:
        0,{chain_no_1},0,R0A;0,{chain_no_1},0,R0B;...;0,{chain_no_2},0,R0A;...
        """
        parts: list[str] = []
        for rru in rru_list:
            chain_no = chain_map.get(rru, 0)
            for port in ports:
                parts.append(f"0,{chain_no},0,{port}")
        return ";".join(parts)

    @staticmethod
    def _format_sector_equipment_antenna(chain_no: int, ports: tuple[str, ...]) -> str:
        return ";".join(f"0,{chain_no},0,{port},RXTX_MODE,MASTER" for port in ports)

    def _build_sector_key(
        self,
        record: GSMCellRecord | LTECellRecord,
        rru_profiles: dict[str, dict[str, Any]],
    ) -> tuple[str, str]:
        """Строит ключ сектора (band_group, marker) единообразно.

        Если в записи есть ret_name с номером антенны (a1, a3, a5),
        маркер формируется из номера антенны (например «a3»).
        Иначе используется старая логика извлечения маркера из cell_name.
        """
        band_group = self._resolve_sector_band_group(record, rru_profiles)
        antenna_number = extract_antenna_number(getattr(record, "ret_name", ""))
        if antenna_number is not None:
            marker = f"a{antenna_number}"
        else:
            marker = self._extract_sector_marker(record.cell_name)
        return (band_group, marker)

    @staticmethod
    def _extract_sector_marker(cell_name: str) -> str:
        """Извлекает номер сектора из имени ячейки."""
        text = str(cell_name or "").strip()
        match = re.search(r"_(\d+)(?:_[A-Za-z0-9]+)?$", text)
        if match:
            return match.group(1)
        return text or "unknown"

    @staticmethod
    def _pick_ne_name(gsm_cells: list[GSMCellRecord], lte_cells: list[LTECellRecord]) -> str:
        for record in lte_cells:
            if record.ne_name:
                return record.ne_name
        for record in gsm_cells:
            if record.ne_name:
                return record.ne_name
        return ""
