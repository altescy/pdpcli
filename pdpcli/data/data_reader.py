from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
from sqlalchemy import create_engine

import colt
import pandas

from pdpcli.exceptions import ConfigurationError


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


@DataReader.register("sql")
class SqlDataReader(DataReader):
    def __init__(self, dsn, **kwargs) -> None:
        self._dsn = dsn
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        with open(file_path) as fp:
            query = fp.read()
        engine = create_engine(self._dsn)
        with engine.connect() as connection:
            return pandas.read_sql(query, connection, **self._kwargs)
