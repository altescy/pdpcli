from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any, Optional, Union

import minato
import pandas
from sqlalchemy import create_engine

from pdpcli import util
from pdpcli.exceptions import ConfigurationError
from pdpcli.registrable import RegistrableWithFile


class DataReader(RegistrableWithFile):
    def read(self, file_path: Union[str, Path]) -> pandas.DataFrame:
        raise NotImplementedError


@DataReader.register("csv", extensions=[".csv"])
class CsvDataReader(DataReader):
    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = util.filter_kwargs(pandas.read_csv, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

    def read(self, file_path: Union[str, Path]) -> pandas.DataFrame:
        file_path = minato.cached_path(file_path)
        df = pandas.read_csv(file_path, **self._kwargs)
        return df


@DataReader.register("tsv", extensions=[".tsv"])
class TsvDataReader(CsvDataReader):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["sep"] = "\t"
        super().__init__(*args, **kwargs)


@DataReader.register("json", extensions=[".json"])
class JsonDataReader(DataReader):
    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = util.filter_kwargs(pandas.read_json, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

    def read(self, file_path: Union[str, Path]) -> pandas.DataFrame:
        file_path = minato.cached_path(file_path)
        df = pandas.read_json(file_path, **self._kwargs)
        return df


@DataReader.register("jsonl", extensions=[".jsonl"])
class JsonLinesDataReader(JsonDataReader):
    def __init__(self, **kwargs: Any) -> None:
        kwargs["orient"] = "records"
        kwargs["lines"] = True
        super().__init__(**kwargs)


@DataReader.register("pickle", extensions=[".pkl", ".pickle"])
class PickleDataReader(DataReader):
    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = util.filter_kwargs(pandas.read_pickle, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

    def read(self, file_path: Union[str, Path]) -> pandas.DataFrame:
        file_path = minato.cached_path(file_path)
        df = pandas.read_pickle(file_path, **self._kwargs)
        return df


@DataReader.register("sql", extensions=[".sql"])
class SqlDataReader(DataReader):
    DSN_KEY = "PDPCLI_SQL_DATA_READER_DSN"

    def __init__(self, dsn: Optional[str] = None, **kwargs: Any) -> None:
        dsn = dsn or os.environ.get(self.DSN_KEY)
        if dsn is None:
            raise ConfigurationError("DSN not specifiled")

        self._dsn = dsn
        self._kwargs = util.filter_kwargs(pandas.read_sql, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

    def read(self, file_path: Union[str, Path]) -> pandas.DataFrame:
        with minato.open(file_path) as fp:
            query = fp.read()
        engine = create_engine(self._dsn)
        with engine.connect() as connection:
            return pandas.read_sql(query, connection, **self._kwargs)
