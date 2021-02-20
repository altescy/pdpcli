from __future__ import annotations
from pathlib import Path

import colt
import pandas


class DataWriter(colt.Registrable):
    def write(self, df: pandas.DataFrame, file_path: Path) -> None:
        raise NotImplementedError


@DataWriter.register("csv")
class CsvDataWriter(DataWriter):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = {"index": False}
        self._kwargs.update(kwargs)

    def write(self, df: pandas.DataFrame, file_path: Path) -> None:
        df.to_csv(file_path, *self._args, **self._kwargs)


@DataWriter.register("json")
class JsonDataWriter(DataWriter):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def write(self, df: pandas.DataFrame, file_path: Path) -> None:
        df.to_json(file_path, *self._args, **self._kwargs)


@DataWriter.register("pickle")
class PickleDataWriter(DataWriter):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def write(self, df: pandas.DataFrame, file_path: Path) -> None:
        df.to_pickle(file_path, *self._args, **self._kwargs)
