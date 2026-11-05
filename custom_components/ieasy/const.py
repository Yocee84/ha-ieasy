"""Constants for the Hiconics iEasy+ integration."""

DOMAIN = "ieasy"
DEFAULT_BASE_URL = "https://ieasy.midea.com/"
DEFAULT_SITE_NAME = "INFO_REGION_COUNTRY_R_Europe"
APP_ID = "1017"
SCAN_INTERVAL_SECONDS = 60
SETTINGS_EVERY = 10  # polls between two reads of the settings tree

CONF_BASE_URL = "base_url"
CONF_SITE_NAME = "site_name"
CONF_LANGUAGE = "language"

# Language of entity names and help texts, chosen per config entry.
LANGUAGES = {"en": "English", "hu": "Magyar"}

CODE_OK = "COMMON_SUCCESS_200"

# Production sites shipped with iEasy+ 1.1.5 (same list as the public
# v1/sys/index/server/sites endpoint). All of them use ieasy.midea.com;
# only the site name sent in the ems_site_name header differs.
SITES = [
    "INFO_REGION_COUNTRY_R_Europe",
    "INFO_REGION_COUNTRY_C_Australia",
    "Modbus_New_Zealand",
    "Modbus_North_America",
    "Register_Latin_America",
    "Register_Asia_Pacific_Central_Asia",
    "INFO_REGION_COUNTRY_C_India",
    "INFO_REGION_COUNTRY_R_Africa",
]

UNLOCK_SECONDS = 300  # writes are refused unless "Settings unlocked" was switched on in the last 5 minutes
DEBOUNCE_SECONDS = 2  # quick repeated changes of one setting: only the last value is sent

# Point codes of the six TOU slots: (function, start, end, power limit, SOC limit).
TOU_SLOTS = (
    ("13779", "13763", "13764", "23024", "23036"), ("13780", "13765", "13766", "23026", "23037"),
    ("13781", "13767", "13768", "23028", "23038"), ("13782", "13769", "13770", "23030", "23039"),
    ("13783", "13775", "13776", "23032", "23040"), ("13784", "13777", "13778", "23034", "23041"),
)

# Point codes of the six SG Ready schedule slots: (mode, start, end).
SG_READY_SLOTS = (
    ("23160", "23148", "23149"), ("23161", "23150", "23151"), ("23162", "23152", "23153"),
    ("23163", "23154", "23155"), ("23164", "23156", "23157"), ("23165", "23158", "23159"),
)
