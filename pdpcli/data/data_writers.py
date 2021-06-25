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


class DataWriter(RegistrableWithFile):
    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        raise NotImplementedError


@DataWriter.register("csv", extensions=[".csv"])
class CsvDataWriter(DataWriter):
    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = util.filter_kwargs(pandas.DataFrame.to_csv, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

        if "index" not in self._kwargs:
            self._kwargs["index"] = False

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        with minato.open(file_path, "w") as fp:
            df.to_csv(fp, **self._kwargs)


@DataWriter.register("tsv", extensions=[".tsv"])
class TsvDataWriter(CsvDataWriter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["sep"] = "\t"
        super().__init__(*args, **kwargs)


@DataWriter.register("json", extensions=[".json"])
class JsonDataWriter(DataWriter):
    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = util.filter_kwargs(pandas.DataFrame.to_json, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        with minato.open(file_path, "w") as fp:
            df.to_json(fp, **self._kwargs)


@DataWriter.register("jsonl", extensions=[".jsonl"])
class JsonLinesDataWriter(JsonDataWriter):
    def __init__(self, **kwargs: Any) -> None:
        kwargs["orient"] = "records"
        kwargs["lines"] = True
        super().__init__(**kwargs)


@DataWriter.register("pickle", extensions=[".pkl", ".pickle"])
class PickleDataWriter(DataWriter):
    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = util.filter_kwargs(pandas.DataFrame.to_pickle, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        with minato.open(file_path, "wb") as fp:
            df.to_pickle(fp, **self._kwargs)


@DataWriter.register("sql")
class SqlDataWriter(DataWriter):
    DSN_KEY = "PDPCLI_SQL_DATA_WRITER_DSN"

    def __init__(
        self,
        dsn: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        dsn = dsn or os.environ.get(self.DSN_KEY)
        if dsn is None:
            raise ConfigurationError("DSN not specifiled")

        self._dsn = dsn
        self._kwargs = util.filter_kwargs(pandas.DataFrame.to_sql, kwargs)

        given_args = set(kwargs)
        valid_args = set(self._kwargs)
        if set(given_args) != set(valid_args):
            warnings.warn("some arguments are ignored: " f"{given_args - valid_args}")

    def write(self, df: pandas.DataFrame, file_path: Union[str, Path]) -> None:
        table_name = str(file_path)
        engine = create_engine(self._dsn, echo=False)
        with engine.begin() as connection:
            df.to_sql(table_name, con=connection, **self._kwargs)
