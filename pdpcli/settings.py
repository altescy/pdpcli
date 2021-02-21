from pathlib import Path

# colt settings
DEFAULT_COLT_SETTING = {
    "typekey": "type",
}

# plugin settings
LOCAL_PLUGINS_FILENAME = ".pdpcli_plugins"
GLOBAL_PLUGINS_FILENAME = str(Path.home() / ".pdpcli" / "plugins")
