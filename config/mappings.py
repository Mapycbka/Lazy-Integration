"""Настройки соответствий между исходными Excel-файлами и шаблоном."""

TRANSPORT_SOURCE_SHEET = "ip-план"
TARGET_TRANSPORT_SHEET = "Base Station Transport Data"
SITE_CONFIGURATION_SHEET = "Конфигурация сайта"
FOUR_G_DATA_SHEET = "4G_Data"
NE_VERSION_SHEET = "NE Version"

# Соответствия колонок ТС -> шаблон.
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

DI_NE_NAME_COLUMN = "Ne Name(name@OSS)"
ENODEB_ID_SOURCE_COLUMN = "eNodeBID"
ENODEB_ID_TARGET_COLUMN = "*eNodeB ID"
ADJNODE_TARGET_COLUMN = "ADJNODE (ID)"
SCTPLNK_TARGET_COLUMN = "SCTPLNK(BSC) (ID1)"
NE_VERSION_NAME_COLUMN = "NE Name"

# Допустимые альтернативные имена столбцов в шаблоне.
TARGET_COLUMN_ALIASES = {
    ENODEB_ID_TARGET_COLUMN: [ENODEB_ID_TARGET_COLUMN],
    ADJNODE_TARGET_COLUMN: [ADJNODE_TARGET_COLUMN, "ID"],
    SCTPLNK_TARGET_COLUMN: [SCTPLNK_TARGET_COLUMN, "ID1"],
    "Transport Port": ["Transport Port", "Port"],
}

# Пример регулярных выражений для поиска старых версий ПО в шаблоне.
BTS_PATTERN = r"BTS[0-9_ ]+V100R\d{3}C\d{2}SPC\d{3}"
BSC_PATTERN = r"BSC\d+V100R\d{3}C\d{2}SPC\d{3}"
