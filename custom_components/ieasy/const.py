"""Constants for the Hiconics iEasy+ integration."""

DOMAIN = "ieasy"
DEFAULT_BASE_URL = "https://ieasy.midea.com/"
DEFAULT_SITE_NAME = "INFO_REGION_COUNTRY_R_Europe"
APP_ID = "1017"
SCAN_INTERVAL_SECONDS = 60
SETTINGS_EVERY = 10  # polls between two reads of the settings tree

CONF_BASE_URL = "base_url"
CONF_SITE_NAME = "site_name"

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
