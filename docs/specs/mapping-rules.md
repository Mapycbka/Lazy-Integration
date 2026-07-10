# Правила сопоставлений ДИ/ТС → шаблон

Канонический справочник правил маппинга данных из Design Input (ДИ) и Transport Sheet (ТС) в конфигурационный шаблон Huawei. Файл предназначен как для людей (читаемые таблицы), так и для программ (встроенные ```yaml-блоки с ключами, совпадающими с именами в `core/constants.py`).

> **Как использовать программно.** Извлеките все блоки ```yaml регулярным выражением ` ```yaml\n([\s\S]*?)\n``` `, распарсите каждый как YAML-документ. Ключи верхнего уровня совпадают с именами констант в исходниках. Алгоритмические правила даны псевдокодом в ```text-блоках — их нужно реализовать вручную.

---

## Содержание

1. [Соглашения о нормализации](#1-соглашения-о-нормализации)
2. [Алиасы листов](#2-алиасы-листов)
3. [География](#3-география)
4. [Поля ДИ: GSM (2G_BTS_Data)](#4-поля-ди-gsm-2g_bts_data)
5. [Поля ДИ: LTE (4G_Data)](#5-поля-ди-lte-4g_data)
6. [Поля ТС: источник (ip-план)](#6-поля-тс-источник-ip-план)
7. [Маппинг ТС → шаблон](#7-маппинг-тс--шаблон)
8. [Целевые поля транспорта](#8-целевые-поля-транспорта)
9. [Колонки шаблона и их алиасы](#9-колонки-шаблона-и-их-алиасы)
10. [Структура листов шаблона](#10-структура-листов-шаблона)
11. [Полный маппинг лист → колонка → источник](#11-полный-маппинг-лист--колонка--источник)
12. [Извлечение значений из ячеек](#12-извлечение-значений-из-ячеек)
13. [Идентификаторы: NE Name и BSC NAME](#13-идентификаторы-ne-name-и-bsc-name)
14. [DI-derived поля транспорта](#14-di-derived-поля-транспорта)
15. [Band → Frequency band](#15-band--frequency-band)
16. [Bandwidth → CELL_BW](#16-bandwidth--cell_bw)
17. [TxRxmode → RX/TX каналы](#17-txrxmode--rxtx-каналы)
18. [RF Unit Working Mode по диапазону](#18-rf-unit-working-mode-по-диапазону)
19. [Chain No. (RRUCHAIN)](#19-chain-no-rruchain)
20. [Определение диапазона RRU](#20-определение-диапазона-rru)
21. [Справочник RRU_MODEL_TO_BAND](#21-справочник-rru_model_to_band)
22. [Sector Equipment ID](#22-sector-equipment-id)
23. [Shared 2T2R Split](#23-shared-2t2r-split)
24. [Порты антенн по TxRx (default)](#24-порты-антенн-по-txrx-default)
25. [Форматы Sector Antenna / Sector Equipment Antenna](#25-форматы-sector-antenna--sector-equipment-antenna)
26. [Номер сектора (RetName / cell_name)](#26-номер-сектора-retname--cell_name)
27. [GSM Cell: вычисляемые поля](#27-gsm-cell-вычисляемые-поля)
28. [Замена версий ПО](#28-замена-версий-по)
29. [Порядок пайплайна генерации](#29-порядок-пайплайна-генерации)
30. [Источники](#30-источники)

---

## 1. Соглашения о нормализации

Все сравнения имён листов и заголовков идут по **нормализованным** строкам.

| Функция | Правило |
|---------|---------|
| `normalize_header` | `str.trim()`, схлопывание пробелов в один, `casefold()` |
| `_normalize_sheet_name` (поиск листа) | `casefold().trim()`, удалить символы ` ` `-` `_` `–` `—` `.` `,` `(` `)` |
| `find_best_header_row` | Проверяются первые `max_scan_rows` (по умолчанию 8) строк листа. Для каждой строится `header_map` и считается score = число заголовков, попавших в множество кандидатов. Выбирается строка с максимальным score. |
| `resolve_header_name` | По построенному `header_map` ищет реальное имя заголовка по списку алиасов (нормализованное сравнение). |

```yaml
normalization:
  header: "str(value).strip(); re.sub(r'\\s+',' ',v); v.casefold()"
  sheet_name: "casefold().strip(); удалить [' ','-','_','–','—','.',',','(',')']"
  header_scan_rows: 8
```

---

## 2. Алиасы листов

Поиск листа в книге идёт по нормализованному имени: перебираются алиасы, первый совпавший возвращает реальное имя листа.

### ДИ (Design Input)

| Каноническое имя | Алиасы |
|------------------|--------|
| `2G_BTS_Data` | `2G BTS Data`, `2G BTS`, `2G` |
| `4G_Data` | `4G Data`, `LTE Data`, `LTE`, `4G` |
| `Конфигурация сайта` | `конфигурация сайта`, `Конфиг сайта`, `Site Configuration`, `site configuration` |

### ТС (Transport Sheet)

| Каноническое имя | Алиасы |
|------------------|--------|
| `ip-план` | `ip план`, `ip-plan`, `ip_plan`, `ipplan`, `IP-план`, `IP план`, `IP PLAN`, `ip plan`, `IP plan`, `IP-Plan`, `ИД БС-ТС`, `Заявка РЦМ`, `IP BTS`, `IP BS` |

### Шаблон (Template)

| Каноническое имя | Алиасы |
|------------------|--------|
| `NE Version` | `NE_VERSION`, `NE version` |
| `Auto Deployment` | `AutoDeployment`, `AUTO DEPLOYMENT` |
| `Base Station Transport Data` | `BaseStationTransportData`, `Transport Data` |
| `GSM Cell` | `GSM_CELL`, `GSMCell` |
| `GTRXGROUP` | `GTRX Group`, `GTRXGROUP(NODE)` |
| `LTE Cell` | `LTE_CELL`, `LTECell` |
| `BBP(NODE)` | `BBP`, `BBP NODE` |
| `RRUCHAIN(NODE)` | `RRUCHAIN`, `RRUCHAIN NODE` |
| `RRU(NODE)` | `RRU`, `RRU NODE` |
| `SECTOR(NODE)` | `SECTOR`, `SECTOR NODE` |
| `SECTOREQM(NODE)` | `SECTOREQM`, `SECTOREQM NODE` |

```yaml
GSM_DI_SHEET_ALIASES: ["2G_BTS_Data", "2G BTS Data", "2G BTS", "2G"]
LTE_DI_SHEET_ALIASES: ["4G_Data", "4G Data", "LTE Data", "LTE", "4G"]
SITE_CONFIGURATION_SHEET_ALIASES: ["Конфигурация сайта", "конфигурация сайта", "Конфиг сайта", "Site Configuration", "site configuration"]
TRANSPORT_SHEET_ALIASES: ["ip-план", "ip план", "ip-plan", "ip_plan", "ipplan", "IP-план", "IP план", "IP PLAN", "ip plan", "IP plan", "IP-Plan", "ИД БС-ТС", "Заявка РЦМ", "IP BTS", "IP BS"]
TEMPLATE_SHEET_ALIASES:
  "NE Version": ["NE Version", "NE_VERSION", "NE version"]
  "Auto Deployment": ["Auto Deployment", "AutoDeployment", "AUTO DEPLOYMENT"]
  "Base Station Transport Data": ["Base Station Transport Data", "BaseStationTransportData", "Transport Data"]
  "GSM Cell": ["GSM Cell", "GSM_CELL", "GSMCell"]
  "GTRXGROUP": ["GTRXGROUP", "GTRX Group", "GTRXGROUP(NODE)"]
  "LTE Cell": ["LTE Cell", "LTE_CELL", "LTECell"]
  "BBP(NODE)": ["BBP(NODE)", "BBP", "BBP NODE"]
  "RRUCHAIN(NODE)": ["RRUCHAIN(NODE)", "RRUCHAIN", "RRUCHAIN NODE"]
  "RRU(NODE)": ["RRU(NODE)", "RRU", "RRU NODE"]
  "SECTOR(NODE)": ["SECTOR(NODE)", "SECTOR", "SECTOR NODE"]
  "SECTOREQM(NODE)": ["SECTOREQM(NODE)", "SECTOREQM", "SECTOREQM NODE"]
```

---

## 3. География

| Тип площадки | Описание |
|--------------|----------|
| `12mbb` | Центр |
| `13mbb` | Северо-Запад |

| Тип BBU | Значения |
|---------|----------|
| BBU | `3900`, `5900` |

| 12mbb (Центр) | 13mbb (Северо-Запад) |
|----------------|----------------------|
| Владимир | Архангельск |
| Иваново | Великий Новгород |
| Калуга | Калининград |
| Кострома | Мурманск |
| Рязань | Петрозаводск |
| Смоленск | Псков |
| Тверь | Санкт-Петербург |
| Тула | Череповец-Вологда |
| Ярославль | |

```yaml
SITE_TYPES: ["12mbb", "13mbb"]
BBU_TYPES: ["3900", "5900"]
REGIONS_BY_SITE_TYPE:
  "12mbb": ["Владимир", "Иваново", "Калуга", "Кострома", "Рязань", "Смоленск", "Тверь", "Тула", "Ярославль"]
  "13mbb": ["Архангельск", "Великий Новгород", "Калининград", "Мурманск", "Петрозаводск", "Псков", "Санкт-Петербург", "Череповец-Вологда"]
```

---

## 4. Поля ДИ: GSM (2G_BTS_Data)

Поля, читаемые из листа `2G_BTS_Data` для построения GSM-записей. Обязательные поля при отсутствии вызывают `ValidationError` (строка пропускается с warning).

| Поле модели | Алиасы колонок | Обяз. |
|--------------|-----------------|-------|
| `ci` | `CI` | да |
| `cell_name` | `CellName`, `Cell Name` | да |
| `lac` | `LAC` | да |
| `ncc` | `NCC` | да |
| `bcc` | `BCC` | да |
| `rac` | `RAC` | да |
| `bcch_frequency` | `BCCH Frequency` | да |
| `power` | `Power, 0.1dbm(per TRX)`, `Power` | да |
| `rru` | `RRU` | да |
| `ret_name` | `RetName`, `Ret Name`, `RETName` | нет |
| `band` | `Band`, `Band (HW)`, `Диапазон` | нет |
| `gsm_freq_band` | `FREQ BAND (900/1800)`, `FREQ BAND`, `Freq Band` | нет |
| `txrx_mode` | `TxRxmode`, `TxRxMode` | нет |
| `ne_name` | `Ne Name(name@OSS)`, `NE Name`, `NodeB Name`, `eNodeB Name` | нет |
| `source_chain_no` | `*Chain No. (RRUCHAIN(NODE))`, `*Chain No.`, `Chain No.` | нет |

```yaml
GSM_REQUIRED_FIELDS:
  ci: ["CI"]
  cell_name: ["CellName", "Cell Name"]
  lac: ["LAC"]
  ncc: ["NCC"]
  bcc: ["BCC"]
  rac: ["RAC"]
  bcch_frequency: ["BCCH Frequency"]
  power: ["Power, 0.1dbm(per TRX)", "Power"]
  rru: ["RRU"]
GSM_OPTIONAL_FIELDS:
  ret_name: ["RetName", "Ret Name", "RETName"]
OPTIONAL_COMMON_FIELDS:
  ne_name: ["Ne Name(name@OSS)", "NE Name", "NodeB Name", "eNodeB Name"]
  band: ["Band", "Band (HW)", "Диапазон"]
  gsm_freq_band: ["FREQ BAND (900/1800)", "FREQ BAND", "Freq Band"]
  txrxmode: ["TxRxmode", "TxRxMode"]
  chain_no: ["*Chain No. (RRUCHAIN(NODE))", "*Chain No.", "Chain No."]
```

---

## 5. Поля ДИ: LTE (4G_Data)

Поля, читаемые из листа `4G_Data` для построения LTE-записей.

| Поле модели | Алиасы колонок | Обяз. |
|--------------|-----------------|-------|
| `local_cell_id` | `Local cell`, `Local Cell`, `*LocalCellID` | да |
| `cell_name` | `Cell Name`, `CellName` | да |
| `tac` | `TAC` | да |
| `band` | `Band (HW)`, `Band` | да |
| `frequency` | `Frequence`, `Frequency`, `Downlink EARFCN` | да |
| `bandwidth` | `Полоса`, `Bandwidth` | да |
| `pci` | `PCI(HW)`, `PCI` | да |
| `root_sequence_index` | `Root sequence index` | да |
| `rsp` | `RSP(HW)`, `RSP` | да |
| `pb` | `Pa Value, dB`, `PB` | да |
| `txrxmode` | `TxRxmode`, `TxRxMode` | да |
| `rru` | `RRU` | да |
| `ret_name` | `RetName`, `Ret Name`, `RETName` | нет |
| `ne_name` | (общие, см. раздел 4) | нет |
| `source_chain_no` | (общие) | нет |

```yaml
LTE_REQUIRED_FIELDS:
  local_cell_id: ["Local cell", "Local Cell", "*LocalCellID"]
  cell_name: ["Cell Name", "CellName"]
  tac: ["TAC"]
  band: ["Band (HW)", "Band"]
  frequency: ["Frequence", "Frequency", "Downlink EARFCN"]
  bandwidth: ["Полоса", "Bandwidth"]
  pci: ["PCI(HW)", "PCI"]
  root_sequence_index: ["Root sequence index"]
  rsp: ["RSP(HW)", "RSP"]
  pb: ["Pa Value, dB", "PB"]
  txrxmode: ["TxRxmode", "TxRxMode"]
  rru: ["RRU"]
LTE_OPTIONAL_FIELDS:
  ret_name: ["RetName", "Ret Name", "RETName"]
```

---

## 6. Поля ТС: источник (ip-план)

Логические поля ТС и их алиасы колонок. Строка заголовков определяется автоматически (см. раздел 1).

| Логическое поле | Алиасы |
|-----------------|--------|
| `MGT IP` | `MGT_IP`, `MGTIP`, `IP MGT`, `MGT OAM IP`, `OMCH` |
| `MGT GW` | `MGT_GW`, `MGT Gateway`, `GW MGT`, `OMCH NH`, `OMCH GW` |
| `MGT Vlan VRF oam` | `MGT VLAN VRF OAM`, `MGT VLAN`, `OMCH Vlan`, `OMCH VLAN` |
| `GSM VLAN_ID VRF 2G` | `GSM VLAN ID VRF 2G`, `GSM VLAN`, `ABIS Vlan`, `ABIS VLAN` |
| `GSM IP_ID` | `GSM IP ID`, `GSM IP`, `ABIS` |
| `GSM GW` | `GSM_GW`, `GSM Gateway`, `ABIS NH`, `ABIS GW` |
| `LTE IP_ID` | `LTE IP ID`, `LTE IP`, `S1`, `S1 IP` |
| `LTE GW` | `LTE_GW`, `LTE Gateway`, `S1 NH`, `S1 GW` |
| `LTE VLAN_ID VRF 4G` | `LTE VLAN ID VRF 4G`, `LTE VLAN`, `S1 Vlan`, `S1 VLAN` |

```yaml
TRANSPORT_SOURCE_HEADER_ALIASES:
  "MGT IP": ["MGT IP", "MGT_IP", "MGTIP", "IP MGT", "MGT OAM IP", "OMCH"]
  "MGT GW": ["MGT GW", "MGT_GW", "MGT Gateway", "GW MGT", "OMCH NH", "OMCH GW"]
  "MGT Vlan VRF oam": ["MGT Vlan VRF oam", "MGT VLAN VRF OAM", "MGT VLAN", "OMCH Vlan", "OMCH VLAN"]
  "GSM VLAN_ID VRF 2G": ["GSM VLAN_ID VRF 2G", "GSM VLAN ID VRF 2G", "GSM VLAN", "ABIS Vlan", "ABIS VLAN"]
  "GSM IP_ID": ["GSM IP_ID", "GSM IP ID", "GSM IP", "ABIS"]
  "GSM GW": ["GSM GW", "GSM_GW", "GSM Gateway", "ABIS NH", "ABIS GW"]
  "LTE IP_ID": ["LTE IP_ID", "LTE IP ID", "LTE IP", "S1", "S1 IP"]
  "LTE GW": ["LTE GW", "LTE_GW", "LTE Gateway", "S1 NH", "S1 GW"]
  "LTE VLAN_ID VRF 4G": ["LTE VLAN_ID VRF 4G", "LTE VLAN ID VRF 4G", "LTE VLAN", "S1 Vlan", "S1 VLAN"]
```

---

## 7. Маппинг ТС → шаблон

Каждое логическое поле ТС переносится в конкретную колонку листа `Base Station Transport Data`. Обработка зависит от типа: IP-адреса → извлечение IPv4, VLAN → извлечение числа, прочие → как есть.

| Источник (ТС) | Цель (шаблон) | Обработка |
|---|---|---|
| `MGT IP` | `OMCH` | extract_ipv4 |
| `MGT GW` | `OMCH NH` | extract_ipv4 |
| `MGT Vlan VRF oam` | `OMCH Vlan` | extract_vlan |
| `GSM VLAN_ID VRF 2G` | `ABIS Vlan` | extract_vlan |
| `GSM IP_ID` | `ABIS` | extract_ipv4 |
| `GSM GW` | `ABIS NH` | extract_ipv4 |
| `LTE IP_ID` | `S1` | extract_ipv4 |
| `LTE GW` | `S1 NH` | extract_ipv4 |
| `LTE VLAN_ID VRF 4G` | `S1 Vlan` | extract_vlan |

```yaml
TRANSPORT_COLUMN_MAPPINGS:
  "MGT IP": {target: "OMCH", extract: "ipv4"}
  "MGT GW": {target: "OMCH NH", extract: "ipv4"}
  "MGT Vlan VRF oam": {target: "OMCH Vlan", extract: "vlan"}
  "GSM VLAN_ID VRF 2G": {target: "ABIS Vlan", extract: "vlan"}
  "GSM IP_ID": {target: "ABIS", extract: "ipv4"}
  "GSM GW": {target: "ABIS NH", extract: "ipv4"}
  "LTE IP_ID": {target: "S1", extract: "ipv4"}
  "LTE GW": {target: "S1 NH", extract: "ipv4"}
  "LTE VLAN_ID VRF 4G": {target: "S1 Vlan", extract: "vlan"}
```

---

## 8. Целевые поля транспорта

Полный список колонок листа `Base Station Transport Data`. IP-цели обрабатываются через `extract_ipv4_address`.

```yaml
TRANSPORT_IP_TARGET_FIELDS: ["OMCH", "OMCH NH", "ABIS", "ABIS NH", "S1", "S1 NH"]
TRANSPORT_TARGET_FIELDS:
  - "*Name"
  - "*BTS Name"
  - "*eNodeB Name"
  - "OMCH"
  - "OMCH NH"
  - "OMCH Vlan"
  - "ABIS"
  - "ABIS NH"
  - "ABIS Vlan"
  - "S1"
  - "S1 NH"
  - "S1 Vlan"
  - "*eNodeB ID"
  - "ADJNODE (ID)"
  - "SCTPLNK(BSC) (ID1)"
  - "Port"
```

---

## 9. Колонки шаблона и их алиасы

Для каждого листа шаблона указаны логические колонки и их алиасы (по которым реальный заголовок ищется в шапке листа).

### NE Version

| Колонка | Алиасы |
|---------|--------|
| `NE Name` | `Node Name`, `eNodeB Name` |

### Auto Deployment

| Колонка | Алиасы |
|---------|--------|
| `*Name` | `Name` |

### Base Station Transport Data

| Колонка | Алиасы |
|---------|--------|
| `*Name` | `Name` |
| `*BTS Name` | `BTS Name` |
| `*eNodeB Name` | `eNodeB Name` |
| `OMCH`, `OMCH NH`, `OMCH Vlan`, `ABIS`, `ABIS NH`, `ABIS Vlan`, `S1`, `S1 NH`, `S1 Vlan` | без алиасов |
| `*eNodeB ID` | без алиасов |
| `ADJNODE (ID)` | `ID` |
| `SCTPLNK(BSC) (ID1)` | `ID1` |
| `Port` | `Transport Port` |

### GSM Cell

| Колонка | Алиасы |
|---------|--------|
| `*BTS Name` | `BTS Name` |
| `*LoCellID` | `*Local Cell ID`, `*LocalCellID` |
| `*CI` | `CI` |
| `BVCI` | — |
| `TRX Group ID` | `*TRX Group ID` |
| `*GSM Cell Name` | `*Cell Name` |
| `*LAC` | `LAC` |
| `NCC`, `BCC` | — |
| `Routing Area` | `RAC` |
| `*Frequency of BCCH` | `Frequency of BCCH` |
| `eGBTS Power Type(0.1dBm)` | `Power` |
| `*Cell Type` | `Cell Type` |

### GTRXGROUP

| Колонка | Алиасы |
|---------|--------|
| `*BTS Name` | `BTS Name` |
| `*TRX Group ID` | `TRX Group ID` |
| `*Local Cell ID` | `*LoCellID`, `CI`, `*CI` |
| `Sector Equipment ID` | `*Sector Equipment ID` |

### LTE Cell

| Колонка | Алиасы |
|---------|--------|
| `*eNodeB Name` | `eNodeB Name` |
| `*Cell ID` | `*LocalCellID`, `*Local Cell ID`, `Cell ID` |
| `*LocalCellID` | `*Local Cell ID`, `*Cell ID`, `Cell ID` |
| `*Cell Name` | `Cell Name` |
| `*Tracking area code` | `Tracking area code` |
| `Frequency band` | — |
| `Downlink EARFCN` | — |
| `Downlink bandwidth`, `Uplink bandwidth` | — |
| `*Physical cell ID` | `Physical cell ID` |
| `Root sequence index` | — |
| `Reference signal power(0.1dBm)` | `RSP` |
| `PB` | `Pa Value, dB` |
| `*Cell transmission and reception mode` | `TxRxmode` |
| `*Sector equipment ID` | `Sector Equipment ID` |

### BBP(NODE)

| Колонка | Алиасы |
|---------|--------|
| `*Slot No.` | `Slot No.` |
| `Head Port No.` | `Port`, `Port No.`, `*Port No.` |

### RRUCHAIN(NODE)

| Колонка | Алиасы |
|---------|--------|
| `*Chain No.` | `Chain No.` |
| `Head Slot No.` | — |
| `Head Port No.` | — |

### RRU(NODE)

| Колонка | Алиасы |
|---------|--------|
| `Subrack No.` | — |
| `*RRU Chain No.` | `RRU Chain No.` |
| `RRU Name` | — |
| `RF Unit Working Mode` | — |
| `Number of RX channels` | — |
| `Number of TX channels` | — |

### SECTOR(NODE)

| Колонка | Алиасы |
|---------|--------|
| `*Sector ID` | `Sector ID` |
| `Sector Name` | — |
| `Sector Antenna` | — |

### SECTOREQM(NODE)

| Колонка | Алиасы |
|---------|--------|
| `*Sector Equipment ID` | `Sector Equipment ID` |
| `*Sector ID` | `Sector ID` |
| `Sector Equipment Antenna` | — |

```yaml
SHEET_HEADER_ALIASES:
  "NE Version":
    "NE Name": ["NE Name", "Node Name", "eNodeB Name"]
  "Auto Deployment":
    "*Name": ["*Name", "Name"]
  "Base Station Transport Data":
    "*Name": ["*Name", "Name"]
    "*BTS Name": ["*BTS Name", "BTS Name"]
    "*eNodeB Name": ["*eNodeB Name", "eNodeB Name"]
    "OMCH": ["OMCH"]
    "OMCH NH": ["OMCH NH"]
    "OMCH Vlan": ["OMCH Vlan"]
    "ABIS Vlan": ["ABIS Vlan"]
    "ABIS": ["ABIS"]
    "ABIS NH": ["ABIS NH"]
    "S1": ["S1"]
    "S1 NH": ["S1 NH"]
    "S1 Vlan": ["S1 Vlan"]
    "*eNodeB ID": ["*eNodeB ID"]
    "ADJNODE (ID)": ["ADJNODE (ID)", "ID"]
    "SCTPLNK(BSC) (ID1)": ["SCTPLNK(BSC) (ID1)", "ID1"]
    "Port": ["Port", "Transport Port"]
  "GSM Cell":
    "*BTS Name": ["*BTS Name", "BTS Name"]
    "*LoCellID": ["*LoCellID", "*Local Cell ID", "*LocalCellID"]
    "*CI": ["*CI", "CI"]
    "BVCI": ["BVCI"]
    "TRX Group ID": ["TRX Group ID", "*TRX Group ID"]
    "*GSM Cell Name": ["*GSM Cell Name", "*Cell Name"]
    "*LAC": ["*LAC", "LAC"]
    "NCC": ["NCC"]
    "BCC": ["BCC"]
    "Routing Area": ["Routing Area", "RAC"]
    "*Frequency of BCCH": ["*Frequency of BCCH", "Frequency of BCCH"]
    "eGBTS Power Type(0.1dBm)": ["eGBTS Power Type(0.1dBm)", "Power"]
    "*Cell Type": ["*Cell Type", "Cell Type"]
  "GTRXGROUP":
    "*BTS Name": ["*BTS Name", "BTS Name"]
    "*TRX Group ID": ["*TRX Group ID", "TRX Group ID"]
    "*Local Cell ID": ["*Local Cell ID", "*LoCellID", "CI", "*CI"]
    "Sector Equipment ID": ["Sector Equipment ID", "*Sector Equipment ID"]
  "LTE Cell":
    "*eNodeB Name": ["*eNodeB Name", "eNodeB Name"]
    "*Cell ID": ["*Cell ID", "*LocalCellID", "*Local Cell ID", "Cell ID"]
    "*LocalCellID": ["*LocalCellID", "*Local Cell ID", "*Cell ID", "Cell ID"]
    "*Cell Name": ["*Cell Name", "Cell Name"]
    "*Tracking area code": ["*Tracking area code", "Tracking area code"]
    "Frequency band": ["Frequency band"]
    "Downlink EARFCN": ["Downlink EARFCN"]
    "Downlink bandwidth": ["Downlink bandwidth"]
    "Uplink bandwidth": ["Uplink bandwidth"]
    "*Physical cell ID": ["*Physical cell ID", "Physical cell ID"]
    "Root sequence index": ["Root sequence index"]
    "Reference signal power(0.1dBm)": ["Reference signal power(0.1dBm)", "RSP"]
    "PB": ["PB", "Pa Value, dB"]
    "*Cell transmission and reception mode": ["*Cell transmission and reception mode", "TxRxmode"]
    "*Sector equipment ID": ["*Sector equipment ID", "Sector Equipment ID"]
  "BBP(NODE)":
    "*Slot No.": ["*Slot No.", "Slot No."]
    "Head Port No.": ["Head Port No.", "Port", "Port No.", "*Port No."]
  "RRUCHAIN(NODE)":
    "*Chain No.": ["*Chain No.", "Chain No."]
    "Head Slot No.": ["Head Slot No."]
    "Head Port No.": ["Head Port No."]
  "RRU(NODE)":
    "Subrack No.": ["Subrack No."]
    "*RRU Chain No.": ["*RRU Chain No.", "RRU Chain No."]
    "RRU Name": ["RRU Name"]
    "RF Unit Working Mode": ["RF Unit Working Mode"]
    "Number of RX channels": ["Number of RX channels"]
    "Number of TX channels": ["Number of TX channels"]
  "SECTOR(NODE)":
    "*Sector ID": ["*Sector ID", "Sector ID"]
    "Sector Name": ["Sector Name"]
    "Sector Antenna": ["Sector Antenna"]
  "SECTOREQM(NODE)":
    "*Sector Equipment ID": ["*Sector Equipment ID", "Sector Equipment ID"]
    "*Sector ID": ["*Sector ID", "Sector ID"]
    "Sector Equipment Antenna": ["Sector Equipment Antenna"]
```

---

## 10. Структура листов шаблона

`SHEET_DEFAULT_START_ROWS` — строка, с которой начинается запись данных (после шапки). `SHEET_FIXED_COLUMNS` — колонки с жёстко зафиксированной позицией (записываются по индексу, а не по заголовку).

| Лист | Start row |
|------|-----------|
| `NE Version` | 2 |
| `Auto Deployment` | 3 |
| `Base Station Transport Data` | 2 |
| `GSM Cell` | 2 |
| `GTRXGROUP` | 2 |
| `LTE Cell` | 2 |
| `BBP(NODE)` | 2 |
| `RRUCHAIN(NODE)` | 2 |
| `RRU(NODE)` | 2 |
| `SECTOR(NODE)` | 2 |
| `SECTOREQM(NODE)` | 2 |

| Лист | Колонка | Позиция (index, 1-based) |
|------|---------|--------------------------|
| `LTE Cell` | `Reference signal power(0.1dBm)` | 38 (AL) |

```yaml
SHEET_DEFAULT_START_ROWS:
  "NE Version": 2
  "Auto Deployment": 3
  "Base Station Transport Data": 2
  "GSM Cell": 2
  "GTRXGROUP": 2
  "LTE Cell": 2
  "BBP(NODE)": 2
  "RRUCHAIN(NODE)": 2
  "RRU(NODE)": 2
  "SECTOR(NODE)": 2
  "SECTOREQM(NODE)": 2
SHEET_FIXED_COLUMNS:
  "LTE Cell":
    "Reference signal power(0.1dBm)": 38
```

---

## 11. Полный маппинг лист → колонка → источник

Каноническая таблица: какая колонка какого листа какое значение получает. Источник — `core/template_writer.py` (`_write_*`) и `core/sector_builder.py`.

### NE Version

| Колонка | Источник значения |
|---------|-------------------|
| `NE Name` | `bundle.ne_name` (из листа `Конфигурация сайта`) |

Записывается одна строка (`single_record_only=True`). Прочие строки в колонке очищаются.

### Auto Deployment

| Колонка | Источник |
|---------|----------|
| `*Name` | `bundle.ne_name` |

### Base Station Transport Data

| Колонка | Источник |
|---------|----------|
| `*Name`, `*BTS Name`, `*eNodeB Name` | `bundle.ne_name` |
| `OMCH`, `OMCH NH`, `ABIS`, `ABIS NH`, `S1`, `S1 NH` | из ТС (`extract_ipv4`) |
| `OMCH Vlan`, `ABIS Vlan`, `S1 Vlan` | из ТС (`extract_vlan`) |
| `*eNodeB ID` | из `eNodeBID` листа `4G_Data` |
| `ADJNODE (ID)` | последняя группа цифр NE Name без ведущих нулей |
| `SCTPLNK(BSC) (ID1)` | `ADJNODE` + `"0"` |
| `Port` | поле формы «Порт транспортной платы» |

### GSM Cell

| Колонка | Источник |
|---------|----------|
| `*BTS Name` | `bundle.ne_name` |
| `*LoCellID` | `record.ci` |
| `*CI` | `record.ci` |
| `BVCI` | `record.ci` |
| `TRX Group ID` | `record.trx_group_id` = `f"{ci}0"` |
| `*GSM Cell Name` | `record.cell_name` |
| `*LAC` | `record.lac` |
| `NCC` | `record.ncc` |
| `BCC` | `record.bcc` |
| `Routing Area` | `record.rac` |
| `*Frequency of BCCH` | `record.bcch_frequency` |
| `eGBTS Power Type(0.1dBm)` | `"400"` (константа) |
| `*Cell Type` | `gsm_freq_band_to_cell_type(record.freq_band)` |

### GTRXGROUP

| Колонка | Источник |
|---------|----------|
| `*BTS Name` | `bundle.ne_name` |
| `*TRX Group ID` | `record.trx_group_id` = `f"{ci}0"` |
| `*Local Cell ID` | `record.ci` |
| `Sector Equipment ID` | `record.sector_equipment_id` |

### LTE Cell

| Колонка | Источник |
|---------|----------|
| `*eNodeB Name` | `bundle.ne_name` |
| `*Cell ID` | `record.local_cell_id` |
| `*LocalCellID` | `record.local_cell_id` |
| `*Cell Name` | `record.cell_name` |
| `*Tracking area code` | `record.tac` |
| `Frequency band` | `record.frequency_band` (из `parse_band_to_frequency_band`) |
| `Downlink EARFCN` | `record.downlink_earfcn` |
| `Downlink bandwidth` | `record.downlink_bandwidth` (из `parse_bandwidth_to_cell_bw`) |
| `Uplink bandwidth` | `record.uplink_bandwidth` (то же) |
| `*Physical cell ID` | `record.physical_cell_id` |
| `Root sequence index` | `record.root_sequence_index` |
| `Reference signal power(0.1dBm)` | `record.reference_signal_power` |
| `PB` | `record.pb` |
| `*Cell transmission and reception mode` | `record.txrx_mode` |
| `*Sector equipment ID` | `record.sector_equipment_id` |

### BBP(NODE)

| Колонка | Источник |
|---------|----------|
| `*Slot No.` | каждое значение из `state.slot_numbers` (по строке на слот) |
| `Head Port No.` | `", ".join(board_ports)` (одна строка на слот, все порты через запятую) |

### RRUCHAIN(NODE)

| Колонка | Источник |
|---------|----------|
| `*Chain No.` | `record.chain_no` |
| `Head Slot No.` | `record.head_slot_no` (из формы / диалога) |
| `Head Port No.` | `record.head_port_no` (из формы / диалога) |

### RRU(NODE)

| Колонка | Источник |
|---------|----------|
| `Subrack No.` | `record.chain_no` (равен `*RRU Chain No.`) |
| `*RRU Chain No.` | `record.chain_no` |
| `RRU Name` | `f"{band}_{index}"` (index — порядковый в группе band) |
| `RF Unit Working Mode` | `BAND_TO_RF_WORKING_MODE[band]` |
| `Number of RX channels` | `parse_txrxmode_to_channels(effective_txrx)[0]` |
| `Number of TX channels` | `parse_txrxmode_to_channels(effective_txrx)[1]` |

### SECTOR(NODE)

| Колонка | Источник |
|---------|----------|
| `*Sector ID` | `record.sector_id` |
| `Sector Name` | `record.sector_name` = `f"{display_band}_{sector_order-1}"` |
| `Sector Antenna` | `record.sector_antenna` = `";".join(f"0,{sector_id},0,{port}")` |

### SECTOREQM(NODE)

| Колонка | Источник |
|---------|----------|
| `*Sector Equipment ID` | `record.sector_equipment_id` |
| `*Sector ID` | `record.sector_id` |
| `Sector Equipment Antenna` | `";".join(f"0,{chain_no},0,{port},RXTX_MODE,MASTER")` |

---

## 12. Извлечение значений из ячеек

Функции нормализации значений ячеек перед записью в шаблон.

| Функция | Описание |
|---------|----------|
| `safe_string(value)` | `str(value).strip()` если не `None`, иначе `""` |
| `extract_ipv4_address(value)` | regex-поиск IPv4; если не найден — возвращает исходную строку |
| `extract_vlan_value(value)` | отрезает текст после `(` и `/`, берёт первое число |

```yaml
extractors:
  safe_string:
    rule: "str(value).strip() if value is not None else ''"
  extract_ipv4_address:
    pattern: "\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"
    fallback: "возвращает исходный текст, если IPv4 не найден"
  extract_vlan_value:
    rule: "отрезать после '(' и '/', взять первое число regex '\\d+'"
    examples:
      - "3702 (vprn 71007000) -> 3702"
      - "3702 / резерв -> 3702"
```

---

## 13. Идентификаторы: NE Name и BSC NAME

| Поле | Лист-источник | Алиасы колонок | Назначение |
|------|---------------|-----------------|------------|
| NE Name | `Конфигурация сайта` | `Ne Name(name@OSS)`, `NE Name`, `NodeB Name`, `eNodeB Name` | лист `NE Version` + глобальная замена по всей книге |
| BSC NAME | `2G_BTS_Data` | `BSC NAME`, `BSC Name`, `BSC_NAME`, `Bsc Name`, `BSC` | только отображение в GUI, в шаблон не пишется |

**Глобальная замена NE Name** (`ReplaceService.replace_ne_name`):

1. На листе `NE Version` в колонке `NE Name` (алиас `NE_VERSION_NAME_COLUMN`) собираются все уникальные старые значения (строки 2..max).
2. В строке 2 пишется новое имя, остальные строки колонки очищаются.
3. По всей книге во всех строковых ячейках старые имена заменяются на новое.
4. После замен удаляются дубликаты вида `A;A`.

```yaml
identifiers:
  ne_name:
    source_sheet_aliases: ["Конфигурация сайта", "конфигурация сайта", "Конфиг сайта", "Site Configuration", "site configuration"]
    source_column_aliases: ["Ne Name(name@OSS)", "NE Name", "NodeB Name", "eNodeB Name"]
    target_sheet: "NE Version"
    target_column: "NE Name"
    NE_VERSION_NAME_COLUMN: "NE Name"
    global_replace: true
    deduplicate_semicolon: true
  bsc_name:
    source_sheet_aliases: ["2G_BTS_Data", "2G BTS Data", "2G BTS", "2G"]
    source_column_aliases: ["BSC NAME", "BSC Name", "BSC_NAME", "Bsc Name", "BSC"]
    target: "только отображение в GUI"
```

---

## 14. DI-derived поля транспорта

Заполняются всегда (даже при пропуске ТС). IP/VLAN-поля остаются пустыми, если ТС не загружен.

| Поле | Значение |
|------|----------|
| `*Name` | NE Name |
| `*BTS Name` | NE Name |
| `*eNodeB Name` | NE Name |
| `*eNodeB ID` | первое непустое из колонок `eNodeBID`, `*eNodeB ID` листа `4G_Data` |
| `ADJNODE (ID)` | последняя группа цифр из NE Name без ведущих нулей (`digits[-1].lstrip("0") or "0"`) |
| `SCTPLNK(BSC) (ID1)` | `f"{adjnode}0"` |
| `Port` | поле формы «Порт транспортной платы» |

```yaml
di_derived_transport:
  enodeb_id_aliases: ["eNodeBID", "*eNodeB ID"]
  adjnode_rule: "последняя группа цифр regex '\\d+' из NE Name, без ведущих нулей; если пусто -> '0'"
  sctplnk_rule: "f'{adjnode}0'"
  name_fields: ["*Name", "*BTS Name", "*eNodeB Name"]
  name_value: "NE Name"
```

---

## 15. Band → Frequency band

`normalize_band` сначала приводится к верхнему регистру, удаляются `МГЦ`/`MHZ`, схлопываются пробелы. Затем `BAND_TO_FREQUENCY_BAND` даёт код.

| Band (нормализованный) | Frequency band |
|------------------------|----------------|
| `2100` | 1 |
| `1800` | 3 |
| `2600` | 7 |
| `900` | 8 |
| `800` | 20 |
| `2600 TDD` | 38 |

**Замены `normalize_band`:** `BAND1`→`2100`, `BAND3`→`1800`, `BAND7`→`2600`, `BAND8`→`900`, `BAND20`→`800`, `BAND38`→`2600 TDD`, `2600TDD`→`2600 TDD`.

```yaml
BAND_TO_FREQUENCY_BAND:
  "2100": 1
  "1800": 3
  "2600": 7
  "900": 8
  "800": 20
  "2600 TDD": 38
normalize_band_replacements:
  "BAND1": "2100"
  "BAND3": "1800"
  "BAND7": "2600"
  "BAND8": "900"
  "BAND20": "800"
  "BAND38": "2600 TDD"
  "2600TDD": "2600 TDD"
  "1800/2100": "1800/2100"
normalize_band_pre: "upper(); удалить 'МГЦ' и 'MHZ'; схлопнуть пробелы"
```

---

## 16. Bandwidth → CELL_BW

Извлекается число из строки полосы, умножается на 5, результат форматируется как `CELL_BW_N{mul}`.

```yaml
bandwidth_to_cell_bw:
  extract_number_pattern: "(\\d+)"
  multiplier: 5
  format: "CELL_BW_N{multiplied}"
  example: "10 -> CELL_BW_N50"
```

---

## 17. TxRxmode → RX/TX каналы

| TxRxmode | RX | TX |
|----------|----|----|
| `2T2R` | 2 | 2 |
| `4T4R` | 4 | 4 |

Неизвестное значение → `ValidationError`.

```yaml
TXRXMODE_TO_CHANNELS:
  "2T2R": [2, 2]
  "4T4R": [4, 4]
```

---

## 18. RF Unit Working Mode по диапазону

| Band | RF Unit Working Mode |
|------|----------------------|
| `800` | `GL` |
| `900` | `GL` |
| `1800` | `GL` |
| `2100` | `UL` |
| `2600` | `GL` |
| `2600 TDD` | `GL` |
| `1800/2100` | `GL` |
| `1800/2100/2600` | `GL` |

```yaml
BAND_TO_RF_WORKING_MODE:
  "800": "GL"
  "900": "GL"
  "1800": "GL"
  "2100": "UL"
  "2600": "GL"
  "2600 TDD": "GL"
  "1800/2100": "GL"
  "1800/2100/2600": "GL"
```

---

## 19. Chain No. (RRUCHAIN)

Каждому уникальному RRU назначается `*Chain No.`. Приоритет правил: региональные переопределения (`CHAIN_NO_RULES_BY_REGION`) → общие правила по типу площадки (`CHAIN_NO_RULES`).

**12mbb (Центр):**

| Band | Chain No. |
|------|-----------|
| 900 | 90 |
| 1800 | 180 |
| 2100 | 210 |
| 2600 | 240 |
| 2600 TDD | 230 |
| 1800/2100 | 200 |
| 1800/2100/2600 | 200 |

**13mbb (Северо-Запад):**

| Band | Chain No. |
|------|-----------|
| 800 | 80 |
| 900 | 120 |
| 1800 | 140 |
| 2100 | 60 |
| 2600 | 150 |
| 2600 TDD | 180 |
| 1800/2100 | 200 |
| 1800/2100/2600 | 200 |

**Переопределение для Калининграда (13mbb):**

| Band | Chain No. |
|------|-----------|
| 1800 | 130 |
| 2100 | 140 |
| 2600 | 160 |
| 1800/2100 | 200 |
| 1800/2100/2600 | 200 |

**Алгоритм назначения:**

```text
1. Для каждого RRU определить resolved_band (см. раздел 20).
2. base_chain_no = CHAIN_NO_RULES_BY_REGION[site_type][region].get(resolved_band)
                  or CHAIN_NO_RULES[site_type][resolved_band]
3. RRU сортируются по antenna_number (из RetName, min) — chain_no совпадает с порядком секторов.
4. Если несколько RRU имеют одинаковый base_chain_no, каждому следующему прибавляется +1:
   chain_map[rru] = base_chain_no + chain_offsets[base_chain_no]
   chain_offsets[base_chain_no] += 1
```

```yaml
CHAIN_NO_RULES:
  "12mbb":
    "900": 90
    "1800": 180
    "2100": 210
    "2600": 240
    "2600 TDD": 230
    "1800/2100": 200
    "1800/2100/2600": 200
  "13mbb":
    "800": 80
    "900": 120
    "1800": 140
    "2100": 60
    "2600": 150
    "2600 TDD": 180
    "1800/2100": 200
    "1800/2100/2600": 200
CHAIN_NO_RULES_BY_REGION:
  "13mbb":
    "Калининград":
      "1800": 130
      "2100": 140
      "2600": 160
      "1800/2100": 200
      "1800/2100/2600": 200
chain_no_algorithm:
  priority: "региональные правила > правила по типу площадки"
  sorting: "по antenna_number из RetName (минимальный номер антенны первым)"
  increment: "если несколько RRU на одном base_chain_no, каждому следующему +1"
```

---

## 20. Определение диапазона RRU

Диапазон RRU определяется в два этапа: сначала по колонке `Band (HW)` (нормализованной), затем — по модели RRU из справочника `RRU_MODEL_TO_BAND`.

**Алгоритм `_resolve_rru_band`:**

```text
1. Собрать множество normalized_bands из записей ДИ для RRU
   (normalize_band(record.band) или normalize_band(record.freq_band) для GSM).
2. Если множество пусто — извлечь модель RRU regex (RRU\d{4}) из имени RRU,
   взять band из RRU_MODEL_TO_BAND.
3. Если множество пусто после шага 2 — ValidationError.
4. Комбинирование:
   - {1800, 2100}            -> "1800/2100"
   - {1800, 2100, 2600}      -> "1800/2100/2600"
   - один диапазон           -> этот диапазон
5. При неоднозначности (>1 диапазона, не комбо):
   preferred_order = ["1800/2100", "2600 TDD", "2600", "2100", "1800", "900", "800"]
   берётся первый совпавший (с warning).
6. Резерв: sorted(normalized_bands)[0].
```

```yaml
resolve_rru_band:
  step1_source: "Band (HW) из ДИ (normalize_band)"
  step1_gsm_fallback: "FREQ BAND (900/1800) для GSM"
  step2_fallback: "RRU_MODEL_TO_BAND по модели regex (RRU\\d{4})"
  combinations:
    "{'1800','2100'}": "1800/2100"
    "{'1800','2100','2600'}": "1800/2100/2600"
  preferred_order: ["1800/2100", "2600 TDD", "2600", "2100", "1800", "900", "800"]
  fallback: "sorted(normalized_bands)[0]"
  rru_model_regex: "(RRU\\d{4})"
```

---

## 21. Справочник RRU_MODEL_TO_BAND

Справочник моделей RRU и их диапазонов. Используется как fallback при пустом/неоднозначном `Band (HW)`.

| Диапазон | Модели |
|----------|--------|
| 700 | `RRU5907`, `RRU5908` |
| 800 | `RRU5305`, `RRU5305e`, `RRU5905`, `RRU3905`, `RRU3906` |
| 900 | `RRU3908`, `RRU3909`, `RRU3938`, `RRU3959`, `RRU5902`, `RRU5502`, `RRU5902e`, `RRU3928` |
| 1800 | `RRU5901`, `RRU5903`, `RRU5909`, `RRU5303`, `RRU5303e`, `RRU3918`, `RRU3929`, `RRU3951`, `RRU5503` |
| 2100 | `RRU5301`, `RRU5304`, `RRU5321`, `RRU5324`, `RRU5504`, `RRU3911`, `RRU3912`, `RRU3921`, `RRU3922`, `RRU3953`, `RRU3954` |
| 2300 | `RRU5336`, `RRU5337` |
| 2600 | `RRU5302`, `RRU5251`, `RRU5302e`, `RRU3915`, `RRU3916`, `RRU3925`, `RRU3926`, `RRU5506` |
| 2600 TDD | `RRU5306`, `RRU5258`, `RRU5338`, `RRU3936`, `RRU3939`, `RRU5509` |
| 3500 | `RRU5901A`, `RRU5903A`, `AAU5612`, `AAU5613` |
| 1800/2100 | `RRU5911`, `RRU5923`, `RRU3933`, `RRU3956` |
| 900/1800 | `RRU5912`, `RRU3931`, `RRU3957` |
| 900/2100 | `RRU5921`, `RRU3932`, `RRU3958` |
| 800/900 | `RRU5913` |
| 1800/2600 | `RRU5915` |
| 900/1800/2100 | `RRU5931`, `RRU3934` |
| 800/900/1800 | `RRU5932` |
| 1800/2100/2600 | `RRU5935` |
| 900/1800/2100/2600 | `RRU5951` |

```yaml
RRU_MODEL_TO_BAND:
  "RRU5907": "700"
  "RRU5908": "700"
  "RRU5305": "800"
  "RRU5305e": "800"
  "RRU5905": "800"
  "RRU3905": "800"
  "RRU3906": "800"
  "RRU3908": "900"
  "RRU3909": "900"
  "RRU3938": "900"
  "RRU3959": "900"
  "RRU5902": "900"
  "RRU5502": "900"
  "RRU5902e": "900"
  "RRU3928": "900"
  "RRU5901": "1800"
  "RRU5903": "1800"
  "RRU5909": "1800"
  "RRU5303": "1800"
  "RRU5303e": "1800"
  "RRU3918": "1800"
  "RRU3929": "1800"
  "RRU3951": "1800"
  "RRU5503": "1800"
  "RRU5301": "2100"
  "RRU5304": "2100"
  "RRU5321": "2100"
  "RRU5324": "2100"
  "RRU5504": "2100"
  "RRU3911": "2100"
  "RRU3912": "2100"
  "RRU3921": "2100"
  "RRU3922": "2100"
  "RRU3953": "2100"
  "RRU3954": "2100"
  "RRU5336": "2300"
  "RRU5337": "2300"
  "RRU5302": "2600"
  "RRU5251": "2600"
  "RRU5302e": "2600"
  "RRU3915": "2600"
  "RRU3916": "2600"
  "RRU3925": "2600"
  "RRU3926": "2600"
  "RRU5506": "2600"
  "RRU5306": "2600 TDD"
  "RRU5258": "2600 TDD"
  "RRU5338": "2600 TDD"
  "RRU3936": "2600 TDD"
  "RRU3939": "2600 TDD"
  "RRU5509": "2600 TDD"
  "RRU5901A": "3500"
  "RRU5903A": "3500"
  "AAU5612": "3500"
  "AAU5613": "3500"
  "RRU5911": "1800/2100"
  "RRU5923": "1800/2100"
  "RRU3933": "1800/2100"
  "RRU3956": "1800/2100"
  "RRU5912": "900/1800"
  "RRU3931": "900/1800"
  "RRU3957": "900/1800"
  "RRU5921": "900/2100"
  "RRU3932": "900/2100"
  "RRU3958": "900/2100"
  "RRU5913": "800/900"
  "RRU5915": "1800/2600"
  "RRU5931": "900/1800/2100"
  "RRU3934": "900/1800/2100"
  "RRU5932": "800/900/1800"
  "RRU5935": "1800/2100/2600"
  "RRU5951": "900/1800/2100/2600"
```

---

## 22. Sector Equipment ID

Формат: `{prefix}{chain_no:03d}{suffix}`.

| Часть | Правило |
|-------|---------|
| prefix | `2` для 2G, `4` для 4G |
| chain_no | номер цепочки RRU (3 цифры с ведущими нулями) |
| suffix | `0` по умолчанию; `1` для диапазона 2100 на multi-band RRU `1800/2100`; `split_index` для shared 2T2R |

**Алгоритм:**

```text
Для 2G:
  sector_equipment_id = build_sector_equipment_id("2G", chain_no_of_record, split_suffix)

Для 4G:
  band_suffix = 1 если resolved_band RRU в ("1800/2100","1800/2100/2600") и band записи == "2100", иначе 0
  sector_equipment_id = build_sector_equipment_id("4G", chain_no_of_record, split_suffix + band_suffix)

Суффикс должен быть в диапазоне 0..9, иначе ValidationError.
```

```yaml
sector_equipment_id:
  format: "{prefix}{chain_no:03d}{suffix}"
  prefix_2g: "2"
  prefix_4g: "4"
  default_suffix: 0
  multi_band_2100_suffix: 1
  multi_band_rru_bands: ["1800/2100", "1800/2100/2600"]
  suffix_range: [0, 9]
```

---

## 23. Shared 2T2R Split

Если один RRU обслуживает несколько 2T2R-секторов одновременно в 2G и 4G, он автоматически переводится в режим `4T4R`, а порты антенн распределяются между подсекторами.

**Условие форсирования 4T4R:** RRU входит в ≥2 секторов, каждый из которых `{2G, 4G}` по source_types и имеет TxRxmode `2T2R` (т.е. кандидат на shared split).

**Паттерны портов `SHARED_2T2R_PORT_PATTERNS`:**

| Индекс | Порты |
|--------|-------|
| 0 | `R0A, R0B` (зарезервирован для standalone 2T2R) |
| 1 | `R0A, R0C` |
| 2 | `R0B, R0D` |
| 3 | `R0C, R0D` |

**Алгоритм:**

```text
pattern_offset = 1  # PATTERN[0] зарезервирован для standalone
Для каждого shared split-сектора (split_index = 0, 1, 2, ...):
  sector_ports = SHARED_2T2R_PORT_PATTERNS[(split_index + pattern_offset) % 4]
Для standalone сектора:
  sector_ports = _default_ports_for_txrx(sector_mode)
```

```yaml
shared_2t2r_split:
  condition: "RRU в >=2 секторах {2G,4G} с TxRx 2T2R"
  forced_mode: "4T4R"
  pattern_offset: 1
  SHARED_2T2R_PORT_PATTERNS:
    - ["R0A", "R0B"]
    - ["R0A", "R0C"]
    - ["R0B", "R0D"]
    - ["R0C", "R0D"]
  reserved_for_standalone_index: 0
```

---

## 24. Порты антенн по TxRx (default)

Стандартные порты антенн для сектора в зависимости от TxRxmode (без shared split).

| TxRxmode | Порты |
|----------|-------|
| `2T2R` | `R0A, R0B` |
| `4T4R` | `R0A, R0B, R0C, R0D` |

Особый случай: 2G на общем 4T4R-RRU без split → поднабор `R0A, R0C`.

```yaml
default_ports_for_txrx:
  "2T2R": ["R0A", "R0B"]
  "4T4R": ["R0A", "R0B", "R0C", "R0D"]
shared_2g_on_4t4r_no_split: ["R0A", "R0C"]
```

---

## 25. Форматы Sector Antenna / Sector Equipment Antenna

| Поле | Формат | Пример |
|------|--------|--------|
| `Sector Antenna` (SECTOR) | `0,{sector_id},0,{port}` для каждого порта, через `;` | `0,91,0,R0A;0,91,0,R0B` |
| `Sector Equipment Antenna` (SECTOREQM) | `0,{chain_no},0,{port},RXTX_MODE,MASTER` для каждого порта, через `;` | `0,91,0,R0A,RXTX_MODE,MASTER;0,91,0,R0B,RXTX_MODE,MASTER` |

```yaml
antenna_formats:
  sector_antenna:
    per_port: "0,{sector_id},0,{port}"
    join: ";"
  sector_equipment_antenna:
    per_port: "0,{chain_no},0,{port},RXTX_MODE,MASTER"
    join: ";"
```

---

## 26. Номер сектора (RetName / cell_name)

Номер сектора определяется двумя способами: из `RetName` (приоритет) или из суффикса `cell_name`.

**`extract_antenna_number` (из RetName):** поддерживает `a1`, `A1`, `а1`, `А1` (кириллица + латиница, без учёта регистра). Буква `a`/`а` должна быть в начале строки или после не-буквенного символа.

**`_extract_sector_marker` (из cell_name):** извлекает последний числовой суффикс после `_`.

**`compute_sector_order_by_antenna`:** антенны сортируются по номеру, порядковый сектор = позиция в отсортированном уникальном ряду.

```yaml
sector_number:
  antenna_number:
    pattern: "(?:^|[^a-zA-Zа-яА-Я])[aаAА](\\d+)"
    supports: "кириллица и латиница, без учёта регистра"
  cell_name_marker:
    pattern: "_(\\d+)(?:_[A-Za-z0-9]+)?$"
  order_by_antenna:
    rule: "sorted(set(antenna_numbers)); порядковый = позиция + 1"
    examples:
      - "[1, 2, 3]       -> {1: 1, 2: 2, 3: 3}"
      - "[1, 3, 5]       -> {1: 1, 3: 2, 5: 3}"
      - "[2, 4, 6]       -> {2: 1, 4: 2, 6: 3}"
      - "[1, 1, 3, 3]    -> {1: 1, 3: 2}"
```

---

## 27. GSM Cell: вычисляемые поля

Поля листа `GSM Cell`, которые вычисляются из других полей, а не берутся напрямую из ДИ.

| Колонка | Правило |
|---------|---------|
| `TRX Group ID` | `f"{ci}0"` |
| `BVCI` | = `CI` |
| `eGBTS Power Type(0.1dBm)` | `"400"` (константа) |
| `*Cell Type` | `gsm_freq_band_to_cell_type(freq_band)` |

**`gsm_freq_band_to_cell_type`:**

| FREQ BAND | Cell Type |
|-----------|-----------|
| `900` | `GSM900` |
| `1800` | `DCS1800` |
| прочее | `GSM900` (резерв) |

```yaml
gsm_cell_computed:
  trx_group_id: "f'{ci}0'"
  bvci: "= CI"
  egbts_power: "400"
  cell_type_map:
    "900": "GSM900"
    "1800": "DCS1800"
  cell_type_fallback: "GSM900"
```

---

## 28. Замена версий ПО

Замены применяются опционально по всей книге после заполнения листов. Логика различается для BTS и BSC.

| Тип | Паттерн | Логика |
|-----|---------|--------|
| BTS | `BTS[0-9_ ]+V100R\d{3}C\d{2}SPC\d{3}` | сохраняется префикс модели (напр. `BTS3900_5900`), заменяется только часть `V100R...` |
| BSC | `BSC\d+V100R\d{3}C\d{2}SPC\d{3}` | полная замена всего совпадения на выбранное значение |

**Дедупликация:** после замены значения вида `A;A` приводятся к `A`. Нормализация для сравнения: `re.sub(r"\s+", " ", v).casefold()`.

**Доступные версии ПО** (из `config/software_options.py`):

```yaml
BTS_PATTERN: "BTS[0-9_ ]+V100R\\d{3}C\\d{2}SPC\\d{3}"
BSC_PATTERN: "BSC\\d+V100R\\d{3}C\\d{2}SPC\\d{3}"
BTS_SOFTWARE_OPTIONS:
  - ""
  - "BTS3900_5900 V100R017C10SPC330"
  - "BTS3900_5900 V100R019C10SPC290"
  - "BTS3900_5900 V100R020C10SPC310"
BSC_SOFTWARE_OPTIONS:
  - ""
  - "BSC6910V100R023C10SPC500"
  - "BSC6910V100R025C10SPC500"
  - "BSC6910V100R026C10SPC500"
software_replacement:
  bts:
    preserve_prefix: true
    version_regex: "V100R\\d{3}C\\d{2}SPC\\d{3}"
  bsc:
    preserve_prefix: false
    full_replace: true
  deduplicate_semicolon:
    normalize: "re.sub(r'\\s+', ' ', v).casefold()"
    rule: "оставить первое вхождение каждого уникального значения, убрать дубли"
```

---

## 29. Порядок пайплайна генерации

Последовательность шагов из `MappingEngine.generate_file`. Порядок важен — правила применяются именно в этой очерёдности.

```text
1.  validate_user_input(state)            — проверка формы
2.  parse_slots(state.slot_numbers_raw)   — нормализация слотов
3.  parse_ports(state.board_ports_raw)    — нормализация портов
4.  open_di_workbook(state.di_path)       — открытие ДИ
5.  resolve_di_sheet_names(workbook)      — поиск листов 2G/4G по алиасам
6.  read_sheet_as_dicts(2G_BTS_Data)      — чтение GSM-строк
7.  read_sheet_as_dicts(4G_Data)          — чтение LTE-строк
8.  build_gsm_records(gsm_rows)           — построение GSM-записей
9.  build_lte_records(lte_rows)           — построение LTE-записей (+ Band/Bandwidth преобразования)
10. extract_ne_name(workbook)             — из листа "Конфигурация сайта"
11. extract_bsc_name(workbook)            — из листа 2G_BTS_Data
12. _build_transport_defaults(lte_rows)   — DI-derived поля (eNodeB ID, ADJNODE, SCTPLNK)
13. Чтение ТС (если не skip):
      resolve_sheet_name(ts, TRANSPORT_SHEET_ALIASES)
      read_sheet_as_dicts с header_aliases
      _build_transport_data (extract_ipv4 / extract_vlan)
      при ошибке → transport_issue_callback (ручной ввод / пропуск / отмена)
14. build_chain_candidates(gsm, lte, state)             — профили RRU + Chain No.
15. _resolve_head_ports(chain_candidates, slots, ports)  — автомат или диалог
16. rru_builder.build_bundle(...)         — RRU chains, RRU records, sectors, sector equipments
17. create_working_copy(template_path)     — копия шаблона в temp/
18. replace_service.replace_ne_name(...)   — NE Name на листе NE Version + глобальная замена
19. _apply_optional_software_replacements  — BTS (preserve prefix) и BSC (full replace)
20. template_writer.write_bundle(...)      — заполнение 11 листов (клон/удаление строк)
21. _apply_optional_software_replacements  — повторно после заполнения листов
22. _strip_external_refs(result_path)      — очистка внешних ссылок [1] из формул
```

```yaml
pipeline_order:
  - "validate_user_input"
  - "parse_slots"
  - "parse_ports"
  - "open_di_workbook"
  - "resolve_di_sheet_names"
  - "read_sheet_as_dicts(2G)"
  - "read_sheet_as_dicts(4G)"
  - "build_gsm_records"
  - "build_lte_records"
  - "extract_ne_name"
  - "extract_bsc_name"
  - "_build_transport_defaults"
  - "read_ts_or_callback"
  - "build_chain_candidates"
  - "_resolve_head_ports"
  - "rru_builder.build_bundle"
  - "create_working_copy"
  - "replace_ne_name"
  - "apply_software_replacements (1st)"
  - "template_writer.write_bundle"
  - "apply_software_replacements (2nd)"
  - "_strip_external_refs"
```

---

## 30. Источники

Канонические источники правил. При изменении кода обновляйте соответствующие разделы этого файла.

| Раздел | Файл:строки |
|--------|-------------|
| 1. Нормализация | `utils/text_utils.py:8-11`, `utils/excel_utils.py:26-62`, `core/excel_loader.py:169-175` |
| 2. Алиасы листов | `core/constants.py:29-87` |
| 3. География | `core/constants.py:101-126`, `config/software_options.py:17` |
| 4. Поля GSM | `core/constants.py:299-313`, `core/sector_builder.py:23-62` |
| 5. Поля LTE | `core/constants.py:315-332`, `core/sector_builder.py:64-139` |
| 6. Поля ТС | `core/constants.py:190-255` |
| 7. Маппинг ТС→шаблон | `core/constants.py:178-188`, `core/mapping_engine.py:203-245` |
| 8. Целевые поля | `core/constants.py:257-283` |
| 9. Колонки шаблона | `core/constants.py:342-435` |
| 10. Структура листов | `core/constants.py:285-297,437-441` |
| 11. Маппинг лист→колонка | `core/template_writer.py:108-245` |
| 12. Извлечение значений | `utils/text_utils.py:19-53` |
| 13. NE Name / BSC | `core/excel_loader.py:127-148`, `services/replace_service.py:16-53`, `config/mappings.py:22-27` |
| 14. DI-derived транспорта | `core/mapping_engine.py:175-201` |
| 15. Band→Frequency | `core/constants.py:162-169`, `utils/text_utils.py:56-72`, `core/transforms.py:37-43` |
| 16. Bandwidth→CELL_BW | `core/transforms.py:46-54` |
| 17. TxRxmode→каналы | `core/constants.py:171-174`, `core/transforms.py:57-63` |
| 18. RF Working Mode | `core/constants.py:539-548` |
| 19. Chain No. | `core/constants.py:128-160`, `core/transforms.py:99-119`, `core/rru_builder.py:161-191` |
| 20. Диапазон RRU | `core/rru_builder.py:577-617` |
| 21. RRU_MODEL_TO_BAND | `core/constants.py:443-537` |
| 22. Sector Equipment ID | `core/transforms.py:12-34`, `core/rru_builder.py:328-365,540-556` |
| 23. Shared 2T2R Split | `core/rru_builder.py:32-37,254-263,275-326,680-713` |
| 24. Порты по TxRx | `core/rru_builder.py:716-719` |
| 25. Форматы Antenna | `core/rru_builder.py:722-746` |
| 26. Номер сектора | `utils/text_utils.py:110-141`, `core/rru_builder.py:748-774` |
| 27. GSM вычисляемые | `core/template_writer.py:118-139`, `core/transforms.py:127-134` |
| 28. Замена ПО | `services/replace_service.py:55-116`, `config/mappings.py:38-39`, `config/software_options.py:1-16` |
| 29. Пайплайн | `core/mapping_engine.py:43-139` |

---

**Source of truth:** `core/constants.py`, `core/transforms.py`, `core/rru_builder.py`, `core/sector_builder.py`, `core/template_writer.py`, `core/mapping_engine.py`, `core/excel_loader.py`, `services/replace_service.py`, `config/mappings.py`, `config/software_options.py`, `utils/text_utils.py`, `utils/excel_utils.py`. При изменении исходников обновляйте этот файл.
