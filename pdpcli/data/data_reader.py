from __future__ import annotations
from pathlib import Path

import colt
import pandas


class DataReader(colt.Registrable):
    def read(self, file_path: Path) -> pandas.DataFrame:
        raise NotImplementedError


@DataReader.register("csv")
class CsvDataReader(DataReader):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        return pandas.read_csv(file_path, *self._args, **self._kwargs)


@DataReader.register("json")
class JsonDataReader(DataReader):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        return pandas.read_json(file_path, *self._args, **self._kwargs)


@DataReader.register("pickle")
class PickleDataReader(DataReader):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        return pandas.read_pickle(file_path, *self._args, **self._kwargs)
