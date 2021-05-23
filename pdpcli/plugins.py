import os
from pathlib import Path
from typing import Iterator, Set, Union

import colt

from pdpcli.settings import GLOBAL_PLUGINS_FILENAME, LOCAL_PLUGINS_FILENAME


def iter_plugins(file_path: Union[str, Path]) -> Iterator[str]:
    with open(file_path) as fp:
        for module_name in fp:
            yield module_name.strip()


def import_plugins() -> None:
    plugins: Set[str] = set()

    if os.path.isfile(LOCAL_PLUGINS_FILENAME):
        for plugin in iter_plugins(LOCAL_PLUGINS_FILENAME):
            plugins.add(plugin)

    if os.path.isfile(GLOBAL_PLUGINS_FILENAME):
        for plugin in iter_plugins(GLOBAL_PLUGINS_FILENAME):
            plugins.add(plugin)

    colt.import_modules(list(plugins))
