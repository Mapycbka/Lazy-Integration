"""Константы, настройки листов и бизнес-правила приложения."""

from __future__ import annotations

from pathlib import Path

APP_TITLE = "Lazy Integration"
WINDOW_MIN_WIDTH = 820
WINDOW_MIN_HEIGHT = 620
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 860

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOGS_DIR / "app.log"
TEMP_DIR = PROJECT_ROOT / "temp"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

DI_REQUIRED_SHEETS = ("2G_BTS_Data", "4G_Data")
TS_REQUIRED_SHEETS = ("ip-план",)
SITE_CONFIGURATION_SHEET = "Конфигурация сайта"
SITE_CONFIGURATION_SHEET_ALIASES = (
    "Конфигурация сайта",
    "конфигурация сайта",
    "Конфиг сайта",
    "Site Configuration",
    "site configuration",
)
GSM_DI_SHEET = "2G_BTS_Data"
GSM_DI_SHEET_ALIASES = (
    "2G_BTS_Data",
    "2G BTS Data",
    "2G BTS",
    "2G",
)

BSC_NAME_ALIASES = (
    "BSC NAME",
    "BSC Name",
    "BSC_NAME",
    "Bsc Name",
    "BSC",
)
LTE_DI_SHEET = "4G_Data"
LTE_DI_SHEET_ALIASES = (
    "4G_Data",
    "4G Data",
    "LTE Data",
    "LTE",
    "4G",
)
TRANSPORT_SHEET = "ip-план"
TRANSPORT_SHEET_ALIASES = (
    "ip-план",
    "ip план",
    "ip-plan",
    "ip_plan",
    "ipplan",
    "IP-план",
    "IP план",
    "IP PLAN",
    "ip plan",
    "IP plan",
    "IP-Plan",
    "ИД БС-ТС",
    "Заявка РЦМ",
    "IP BTS",
    "IP BS",
)
BASE_STATION_TRANSPORT_SHEET = "Base Station Transport Data"
TEMPLATE_SHEET_ALIASES = {
    "NE Version": ("NE Version", "NE_VERSION", "NE version"),
    "Auto Deployment": ("Auto Deployment", "AutoDeployment", "AUTO DEPLOYMENT"),
    "Base Station Transport Data": (
        "Base Station Transport Data",
        "BaseStationTransportData",
        "Transport Data",
    ),
    "GSM Cell": ("GSM Cell", "GSM_CELL", "GSMCell"),
    "GTRXGROUP": ("GTRXGROUP", "GTRX Group", "GTRXGROUP(NODE)"),
    "LTE Cell": ("LTE Cell", "LTE_CELL", "LTECell"),
    "BBP(NODE)": ("BBP(NODE)", "BBP", "BBP NODE"),
    "RRUCHAIN(NODE)": ("RRUCHAIN(NODE)", "RRUCHAIN", "RRUCHAIN NODE"),
    "RRU(NODE)": ("RRU(NODE)", "RRU", "RRU NODE"),
    "SECTOR(NODE)": ("SECTOR(NODE)", "SECTOR", "SECTOR NODE"),
    "SECTOREQM(NODE)": ("SECTOREQM(NODE)", "SECTOREQM", "SECTOREQM NODE"),
}
TEMPLATE_SHEETS = (
    "NE Version",
    "GSM Cell",
    "GTRXGROUP",
    "LTE Cell",
    "Base Station Transport Data",
    "BBP(NODE)",
    "RRUCHAIN(NODE)",
    "RRU(NODE)",
    "SECTOR(NODE)",
    "SECTOREQM(NODE)",
)

SITE_TYPES = ("12mbb", "13mbb")
BBU_TYPES = ("3900", "5900")

REGIONS_BY_SITE_TYPE = {
    "13mbb": (
        "Архангельск",
        "Великий Новгород",
        "Калининград",
        "Мурманск",
        "Петрозаводск",
        "Псков",
        "Санкт-Петербург",
        "Череповец-Вологда",
    ),
    "12mbb": (
        "Владимир",
        "Калуга",
        "Кострома",
        "Рязань",
        "Иваново",
        "Смоленск",
        "Тверь",
        "Тула",
        "Ярославль",
    ),
}

CHAIN_NO_RULES = {
    "13mbb": {
        "800": 80,
        "900": 120,
        "1800": 140,
        "2100": 60,
        "2600": 150,
        "2600 TDD": 180,
        "1800/2100": 200,
        "1800/2100/2600": 200,
    },
    "12mbb": {
        "900": 90,
        "1800": 180,
        "2100": 210,
        "2600": 240,
        "2600 TDD": 230,
        "1800/2100": 200,
        "1800/2100/2600": 200,
    },
}

CHAIN_NO_RULES_BY_REGION = {
    "13mbb": {
        "Калининград": {
            "1800": 130,
            "2100": 140,
            "2600": 160,
            "1800/2100": 200,
            "1800/2100/2600": 200,
        },
    },
}

BAND_TO_FREQUENCY_BAND = {
    "2100": 1,
    "1800": 3,
    "2600": 7,
    "900": 8,
    "800": 20,
    "2600 TDD": 38,
}

TXRXMODE_TO_CHANNELS = {
    "2T2R": (2, 2),
    "4T4R": (4, 4),
}

DEFAULT_SHEET_SCAN_ROWS = 8

TRANSPORT_COLUMN_MAPPINGS = {
    "MGT IP": "OMCH",
    "MGT GW": "OMCH NH",
    "MGT Vlan VRF oam": "OMCH Vlan",
    "GSM VLAN_ID VRF 2G": "ABIS Vlan",
    "GSM IP_ID": "ABIS",
    "GSM GW": "ABIS NH",
    "LTE IP_ID": "S1",
    "LTE GW": "S1 NH",
    "LTE VLAN_ID VRF 4G": "S1 Vlan",
}

TRANSPORT_SOURCE_HEADER_ALIASES = {
    "MGT IP": (
        "MGT IP",
        "MGT_IP",
        "MGTIP",
        "IP MGT",
        "MGT OAM IP",
        "OMCH",
    ),
    "MGT GW": (
        "MGT GW",
        "MGT_GW",
        "MGT Gateway",
        "GW MGT",
        "OMCH NH",
        "OMCH GW",
    ),
    "MGT Vlan VRF oam": (
        "MGT Vlan VRF oam",
        "MGT VLAN VRF OAM",
        "MGT VLAN",
        "OMCH Vlan",
        "OMCH VLAN",
    ),
    "GSM VLAN_ID VRF 2G": (
        "GSM VLAN_ID VRF 2G",
        "GSM VLAN ID VRF 2G",
        "GSM VLAN",
        "ABIS Vlan",
        "ABIS VLAN",
    ),
    "GSM IP_ID": (
        "GSM IP_ID",
        "GSM IP ID",
        "GSM IP",
        "ABIS",
    ),
    "GSM GW": (
        "GSM GW",
        "GSM_GW",
        "GSM Gateway",
        "ABIS NH",
        "ABIS GW",
    ),
    "LTE IP_ID": (
        "LTE IP_ID",
        "LTE IP ID",
        "LTE IP",
        "S1",
        "S1 IP",
    ),
    "LTE GW": (
        "LTE GW",
        "LTE_GW",
        "LTE Gateway",
        "S1 NH",
        "S1 GW",
    ),
    "LTE VLAN_ID VRF 4G": (
        "LTE VLAN_ID VRF 4G",
        "LTE VLAN ID VRF 4G",
        "LTE VLAN",
        "S1 Vlan",
        "S1 VLAN",
    ),
}

TRANSPORT_IP_TARGET_FIELDS = (
    "OMCH",
    "OMCH NH",
    "ABIS",
    "ABIS NH",
    "S1",
    "S1 NH",
)

TRANSPORT_TARGET_FIELDS = (
    "*Name",
    "*BTS Name",
    "*eNodeB Name",
    "OMCH",
    "OMCH NH",
    "OMCH Vlan",
    "ABIS",
    "ABIS NH",
    "ABIS Vlan",
    "S1",
    "S1 NH",
    "S1 Vlan",
    "*eNodeB ID",
    "ADJNODE (ID)",
    "SCTPLNK(BSC) (ID1)",
    "Port",
)

SHEET_DEFAULT_START_ROWS = {
    "NE Version": 2,
    "Auto Deployment": 3,
    "Base Station Transport Data": 2,
    "GSM Cell": 2,
    "GTRXGROUP": 2,
    "LTE Cell": 2,
    "BBP(NODE)": 2,
    "RRUCHAIN(NODE)": 2,
    "RRU(NODE)": 2,
    "SECTOR(NODE)": 2,
    "SECTOREQM(NODE)": 2,
}

GSM_REQUIRED_FIELDS = {
    "ci": ("CI",),
    "cell_name": ("CellName", "Cell Name"),
    "lac": ("LAC",),
    "ncc": ("NCC",),
    "bcc": ("BCC",),
    "rac": ("RAC",),
    "bcch_frequency": ("BCCH Frequency",),
    "power": ("Power, 0.1dbm(per TRX)", "Power"),
    "rru": ("RRU",),
}

GSM_OPTIONAL_FIELDS = {
    "ret_name": ("RetName", "Ret Name", "RETName"),
}

LTE_REQUIRED_FIELDS = {
    "local_cell_id": ("Local cell", "Local Cell", "*LocalCellID"),
    "cell_name": ("Cell Name", "CellName"),
    "tac": ("TAC",),
    "band": ("Band (HW)", "Band"),
    "frequency": ("Frequence", "Frequency", "Downlink EARFCN"),
    "bandwidth": ("Полоса", "Bandwidth"),
    "pci": ("PCI(HW)", "PCI"),
    "root_sequence_index": ("Root sequence index",),
    "rsp": ("RSP(HW)", "RSP"),
    "pb": ("Pa Value, dB", "PB"),
    "txrxmode": ("TxRxmode", "TxRxMode"),
    "rru": ("RRU",),
}

LTE_OPTIONAL_FIELDS = {
    "ret_name": ("RetName", "Ret Name", "RETName"),
}

OPTIONAL_COMMON_FIELDS = {
    "ne_name": ("Ne Name(name@OSS)", "NE Name", "NodeB Name", "eNodeB Name"),
    "band": ("Band", "Band (HW)", "Диапазон"),
    "gsm_freq_band": ("FREQ BAND (900/1800)", "FREQ BAND", "Freq Band"),
    "txrxmode": ("TxRxmode", "TxRxMode"),
    "chain_no": ("*Chain No. (RRUCHAIN(NODE))", "*Chain No.", "Chain No."),
}

SHEET_HEADER_ALIASES = {
    "NE Version": {
        "NE Name": ("NE Name", "Node Name", "eNodeB Name"),
    },
    "GSM Cell": {
        "*BTS Name": ("*BTS Name", "BTS Name"),
        "*LoCellID": ("*LoCellID", "*Local Cell ID", "*LocalCellID"),
        "*CI": ("*CI", "CI"),
        "BVCI": ("BVCI",),
        "TRX Group ID": ("TRX Group ID", "*TRX Group ID"),
        "*GSM Cell Name": ("*GSM Cell Name", "*Cell Name"),
        "*LAC": ("*LAC", "LAC"),
        "NCC": ("NCC",),
        "BCC": ("BCC",),
        "Routing Area": ("Routing Area", "RAC"),
        "*Frequency of BCCH": ("*Frequency of BCCH", "Frequency of BCCH"),
        "eGBTS Power Type(0.1dBm)": ("eGBTS Power Type(0.1dBm)", "Power"),
        "*Cell Type": ("*Cell Type", "Cell Type"),
    },
    "GTRXGROUP": {
        "*BTS Name": ("*BTS Name", "BTS Name"),
        "*TRX Group ID": ("*TRX Group ID", "TRX Group ID"),
        "*Local Cell ID": ("*Local Cell ID", "*LoCellID", "CI", "*CI"),
        "Sector Equipment ID": ("Sector Equipment ID", "*Sector Equipment ID"),
    },
    "LTE Cell": {
        "*eNodeB Name": ("*eNodeB Name", "eNodeB Name"),
        "*Cell ID": ("*Cell ID", "*LocalCellID", "*Local Cell ID", "Cell ID"),
        "*LocalCellID": ("*LocalCellID", "*Local Cell ID", "*Cell ID", "Cell ID"),
        "*Cell Name": ("*Cell Name", "Cell Name"),
        "*Tracking area code": ("*Tracking area code", "Tracking area code"),
        "Frequency band": ("Frequency band",),
        "Downlink EARFCN": ("Downlink EARFCN",),
        "Downlink bandwidth": ("Downlink bandwidth",),
        "Uplink bandwidth": ("Uplink bandwidth",),
        "*Physical cell ID": ("*Physical cell ID", "Physical cell ID"),
        "Root sequence index": ("Root sequence index",),
        "Reference signal power(0.1dBm)": ("Reference signal power(0.1dBm)", "RSP"),
        "PB": ("PB", "Pa Value, dB"),
        "*Cell transmission and reception mode": (
            "*Cell transmission and reception mode",
            "TxRxmode",
        ),
        "*Sector equipment ID": ("*Sector equipment ID", "Sector Equipment ID"),
    },
    "BBP(NODE)": {
        "*Slot No.": ("*Slot No.", "Slot No."),
        "Head Port No.": ("Head Port No.", "Port", "Port No.", "*Port No."),
    },
    "RRUCHAIN(NODE)": {
        "*Chain No.": ("*Chain No.", "Chain No."),
        "Head Slot No.": ("Head Slot No.",),
        "Head Port No.": ("Head Port No.",),
    },
    "RRU(NODE)": {
        "Subrack No.": ("Subrack No.",),
        "*RRU Chain No.": ("*RRU Chain No.", "RRU Chain No."),
        "RRU Name": ("RRU Name",),
        "RF Unit Working Mode": ("RF Unit Working Mode",),
        "Number of RX channels": ("Number of RX channels",),
        "Number of TX channels": ("Number of TX channels",),
    },
    "SECTOR(NODE)": {
        "*Sector ID": ("*Sector ID", "Sector ID"),
        "Sector Name": ("Sector Name",),
        "Sector Antenna": ("Sector Antenna",),
    },
    "SECTOREQM(NODE)": {
        "*Sector Equipment ID": ("*Sector Equipment ID", "Sector Equipment ID"),
        "*Sector ID": ("*Sector ID", "Sector ID"),
        "Sector Equipment Antenna": ("Sector Equipment Antenna",),
    },
    "Base Station Transport Data": {
        "*Name": ("*Name", "Name"),
        "*BTS Name": ("*BTS Name", "BTS Name"),
        "*eNodeB Name": ("*eNodeB Name", "eNodeB Name"),
        "OMCH": ("OMCH",),
        "OMCH NH": ("OMCH NH",),
        "OMCH Vlan": ("OMCH Vlan",),
        "ABIS Vlan": ("ABIS Vlan",),
        "ABIS": ("ABIS",),
        "ABIS NH": ("ABIS NH",),
        "S1": ("S1",),
        "S1 NH": ("S1 NH",),
        "S1 Vlan": ("S1 Vlan",),
        "*eNodeB ID": ("*eNodeB ID",),
        "ADJNODE (ID)": ("ADJNODE (ID)", "ID"),
        "SCTPLNK(BSC) (ID1)": ("SCTPLNK(BSC) (ID1)", "ID1"),
        "Port": ("Port", "Transport Port"),
    },
    "Auto Deployment": {
        "*Name": ("*Name", "Name"),
    },
}

SHEET_FIXED_COLUMNS = {
    "LTE Cell": {
        "Reference signal power(0.1dBm)": 38,  # AL
    },
}

RRU_MODEL_TO_BAND: dict[str, str] = {
    # 700 MHz (Band 28)
    "RRU5907": "700",
    "RRU5908": "700",
    
    # 800 MHz (Band 20 / Band 5)
    "RRU5305": "800",
    "RRU5305e": "800",
    "RRU5905": "800",
    "RRU3905": "800",
    "RRU3906": "800",
    
    # 900 MHz (Band 8)
    "RRU3908": "900",
    "RRU3909": "900",
    "RRU3938": "900",
    "RRU3959": "900",
    "RRU5902": "900",
    "RRU5502": "900",
    "RRU5902e": "900",
    "RRU3928": "900",
    
    # 1800 MHz (Band 3)
    "RRU5901": "1800",
    "RRU5903": "1800",
    "RRU5909": "1800",
    "RRU5303": "1800",
    "RRU5303e": "1800",
    "RRU3918": "1800",
    "RRU3929": "1800",
    "RRU3951": "1800",
    "RRU5503": "1800",
    
    # 2100 MHz (Band 1)
    "RRU5301": "2100",
    "RRU5304": "2100",
    "RRU5321": "2100",
    "RRU5324": "2100",
    "RRU5504": "2100",
    "RRU3911": "2100",
    "RRU3912": "2100",
    "RRU3921": "2100",
    "RRU3922": "2100",
    "RRU3953": "2100",
    "RRU3954": "2100",
    
    # 2300 MHz (Band 30 / Band 40 TDD)
    "RRU5336": "2300",
    "RRU5337": "2300",
    
    # 2600 MHz FDD (Band 7)
    "RRU5302": "2600",
    "RRU5251": "2600",
    "RRU5302e": "2600",
    "RRU3915": "2600",
    "RRU3916": "2600",
    "RRU3925": "2600",
    "RRU3926": "2600",
    "RRU5506": "2600",
    
    # 2600 MHz TDD (Band 38 / Band 41)
    "RRU5306": "2600 TDD",
    "RRU5258": "2600 TDD",
    "RRU5338": "2600 TDD",
    "RRU3936": "2600 TDD",
    "RRU3939": "2600 TDD",
    "RRU5509": "2600 TDD",
    
    # 3500 MHz (Band 42 / Band 78 - 5G NR)
    "RRU5901A": "3500",
    "RRU5903A": "3500",
    "AAU5612": "3500",
    "AAU5613": "3500",
    
    # Multi-band / Combo RRU
    "RRU5901A": "1800/2100", # Пример для комбо, часто требуют уточнения конфигурации
    "RRU5903A": "900/1800",
    "RRU5911": "1800/2100",
    "RRU5912": "900/1800",
    "RRU5913": "800/900",
    "RRU5915": "1800/2600",
    "RRU5921": "900/2100",
    "RRU5923": "1800/2100",
    "RRU5931": "900/1800/2100",
    "RRU5932": "800/900/1800",
    "RRU5935": "1800/2100/2600",
    "RRU5951": "900/1800/2100/2600",
    "RRU3931": "900/1800",
    "RRU3932": "900/2100",
    "RRU3933": "1800/2100",
    "RRU3934": "900/1800/2100",
    "RRU3956": "1800/2100",
    "RRU3957": "900/1800",
    "RRU3958": "900/2100",
}

BAND_TO_RF_WORKING_MODE: dict[str, str] = {
    "800": "GL",
    "900": "GL",
    "1800": "GL",
    "2100": "UL",
    "2600": "GL",
    "2600 TDD": "GL",
    "1800/2100": "GL",
    "1800/2100/2600": "GL",
}
