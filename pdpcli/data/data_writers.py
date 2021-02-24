from __future__ import annotations
from typing import Union
from pathlib import Path
import os

import pandas
from sqlalchemy import create_engine

from pdpcli.exceptions import ConfigurationError
from pdpcli.registrable import RegistrableWithFile


class DataWriter(RegistrableWithFile):
    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        raise NotImplementedError


@DataWriter.register("csv", extensions=[".csv"])
class CsvDataWriter(DataWriter):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = {"index": False}
        self._kwargs.update(kwargs)

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        df.to_csv(file_path, *self._args, **self._kwargs)


@DataWriter.register("tsv", extensions=[".tsv"])
class TsvDataWriter(CsvDataWriter):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["sep"] = "\t"
        super().__init__(*args, **kwargs)


@DataWriter.register("json", extensions=[".json"])
class JsonDataWriter(DataWriter):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        df.to_json(file_path, *self._args, **self._kwargs)


@DataWriter.register("jsonl", extensions=[".jsonl"])
class JsonLinesDataWriter(JsonDataWriter):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["orient"] = "records"
        kwargs["lines"] = True
        super().__init__(*args, **kwargs)


@DataWriter.register("pickle", extensions=[".pkl", ".pickle"])
class PickleDataWriter(DataWriter):
    def __init__(self, *args, **kwargs) -> None:
        self._args = args
        self._kwargs = kwargs

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        df.to_pickle(file_path, *self._args, **self._kwargs)


@DataWriter.register("sql")
class SqlDataWriter(DataWriter):
    DSN_KEY = "PDPCLI_SQL_DATA_WRITER_DSN"

    def __init__(self, dsn: str = None, **kwargs) -> None:
        dsn = dsn or os.environ.get(self.DSN_KEY)
        if dsn is None:
            raise ConfigurationError("DSN not specifiled")
        self._dsn = dsn
        self._kwargs = kwargs

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        table_name = str(file_path)
        engine = create_engine(self._dsn, echo=False)
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, **self._kwargs)
