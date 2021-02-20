from __future__ import annotations
from typing import Dict, List, Optional, Union
from pathlib import Path
from enum import Enum

FILE_EXTENTSIONS: Dict[str, List[str]] = {
    "yaml": [".yml", ".yaml"],
    "json": [".json"],
    "jsonnet": [".jsonnet"],
    "jsonl": [".jsonl"],
    "csv": [".csv"],
    "tsv": [".tsv"],
    "pickle": [".pkl", ".pickle"],
}


class FileType(Enum):
    YAML = "yaml"
    JSON = "json"
    JSONNET = "jsonnet"
    JSONL = "jsonl"
    CSV = "csv"
    TSV = "tsv"
    PICKLE = "pickle"

    @classmethod
    def from_path(cls, file_path: Union[Path, str]) -> Optional[FileType]:
        file_path = Path(file_path)
        ext = file_path.suffix

        for filetype, extensions in FILE_EXTENTSIONS.items():
            if ext in extensions:
                return FileType(filetype)

        return None
