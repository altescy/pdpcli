import re
from pathlib import Path

from pdpcli.filetype import FileType


def camel_to_snake(s: str) -> str:
    underscored = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', underscored).lower()
