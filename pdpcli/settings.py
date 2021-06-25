from pathlib import Path

# colt settings
DEFAULT_COLT_SETTING = {
    "typekey": "type",
}

# pdpcli directory settings
PDPCLI_ROOT = Path.home() / ".pdpcli"

# plugin settings
LOCAL_PLUGINS_FILENAME = ".pdpcli_plugins"
GLOBAL_PLUGINS_FILENAME = PDPCLI_ROOT / "plugins"
