import os
from typing import Set, Iterator

import colt

from pdpcli.settings import LOCAL_PLUGINS_FILENAME, GLOBAL_PLUGINS_FILENAME


def iter_plugins(file_path: str) -> Iterator[str]:
    with open(file_path) as fp:
        for module_name in fp:
            yield module_name.strip()


def import_plugins():
    plugins: Set[str] = set()

    if os.path.isfile(LOCAL_PLUGINS_FILENAME):
        for plugin in iter_plugins(LOCAL_PLUGINS_FILENAME):
            plugins.add(plugin)

    if os.path.isfile(GLOBAL_PLUGINS_FILENAME):
        for plugin in iter_plugins(GLOBAL_PLUGINS_FILENAME):
            plugins.add(plugin)

    colt.import_modules(list(plugins))
