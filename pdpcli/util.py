from typing import Optional
from pathlib import Path
import re

import pdpcli.data
import pdpcli.configs


def camel_to_snake(s: str) -> str:
    underscored = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', underscored).lower()


def infer_data_reader(file_path: Path) -> Optional[pdpcli.data.DataReader]:
    ext = file_path.suffix
    if ext in (".csv", ):
        return pdpcli.data.CsvDataReader()

    if ext in (".tsv", ):
        return pdpcli.data.CsvDataReader(sep="\t")

    if ext in ("jsonl", ):
        return pdpcli.data.JsonDataReader(orient="records")

    if ext in (".pkl", ".pickle"):
        return pdpcli.data.PickleDataReader()

    return None


def infer_data_writer(file_path: Path) -> Optional[pdpcli.data.DataWriter]:
    ext = file_path.suffix
    if ext in (".csv", ):
        return pdpcli.data.CsvDataWriter()

    if ext in (".tsv", ):
        return pdpcli.data.CsvDataWriter(sep="\t")

    if ext in (".jsonl", ):
        return pdpcli.data.JsonDataWriter(orient="records", lines=True)

    if ext in (".pkl", ".pickle"):
        return pdpcli.data.PickleDataWriter()

    return None


def infer_config_reader(
        file_path: Path) -> Optional[pdpcli.configs.ConfigReader]:
    ext = file_path.suffix
    if ext in (".yml", ".yaml"):
        return pdpcli.configs.YamlConfigReader()

    if ext in (".json", ):
        return pdpcli.configs.JsonConfigReader()

    if ext in (".jsonnet", ):
        return pdpcli.configs.JsonnetConfigReader()

    return None
