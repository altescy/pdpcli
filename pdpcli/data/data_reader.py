from __future__ import annotations
from pathlib import Path
import os

import pandas
from sqlalchemy import create_engine

from pdpcli import util
from pdpcli.registrable import RegistrableWithFile
from pdpcli.exceptions import ConfigurationError


class DataReader(RegistrableWithFile):
    def read(self, file_path: Path) -> pandas.DataFrame:
        raise NotImplementedError


@DataReader.register("csv", extensions=[".csv"])
class CsvDataReader(DataReader):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        with util.open_file(file_path) as fp:
            df = pandas.read_csv(fp, *self._args, **self._kwargs)
        return df


@DataReader.register("tsv", extensions=[".tsv"])
class TsvDataReader(CsvDataReader):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["sep"] = "\t"
        super().__init__(*args, **kwargs)


@DataReader.register("json", extensions=[".json"])
class JsonDataReader(DataReader):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        with util.open_file(file_path) as fp:
            df = pandas.read_json(fp, *self._args, **self._kwargs)
        return df


@DataReader.register("jsonl", extensions=[".jsonl"])
class JsonLinesDataReader(JsonDataReader):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["orient"] = "records"
        kwargs["lines"] = True
        super().__init__(*args, **kwargs)


@DataReader.register("pickle", extensions=[".pkl", ".pickle"])
class PickleDataReader(DataReader):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        with util.open_file(file_path, "rb") as fp:
            df = pandas.read_pickle(fp, *self._args, **self._kwargs)
        return df


@DataReader.register("sql", extensions=[".sql"])
class SqlDataReader(DataReader):
    DSN_KEY = "PDPCLI_SQL_DATA_READER_DSN"

    def __init__(self, dsn: str = None, **kwargs) -> None:
        dsn = dsn or os.environ.get(self.DSN_KEY)
        if dsn is None:
            raise ConfigurationError("DSN not specifiled")
        self._dsn = dsn
        self._kwargs = kwargs

    def read(self, file_path: Path) -> pandas.DataFrame:
        with util.open_file(file_path) as fp:
            query = fp.read()
        engine = create_engine(self._dsn)
        with engine.connect() as connection:
            return pandas.read_sql(query, connection, **self._kwargs)
