from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
import importlib

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
        conn = self._get_db_connection()
        return pandas.read_sql(query, conn, **self._kwargs)

    def _get_db_connection(self):
        parsed_dsn = urlparse(self._dsn)
        scheme = parsed_dsn.scheme
        path = parsed_dsn.path
        if scheme == "mysql":
            return self._get_mysql_connection(self._dsn)
        if scheme == "postgres":
            return self._get_pgsql_connection(self._dsn)
        if scheme == "sqlite3":
            return self._get_sqlite_connection(path)
        raise ConfigurationError(f"Invalid database scheme: {scheme}")

    @staticmethod
    def _get_pgsql_connection(dsn: str):
        psycopg2 = importlib.import_module("psycopg2")
        return psycopg2.connect(dsn)  # type: ignore

    @staticmethod
    def _get_mysql_connection(dsn: str):
        MySQLdb = importlib.import_module("MySQLdb")
        return MySQLdb.connect(dsn)  # type: ignore

    @staticmethod
    def _get_sqlite_connection(path: str):
        import sqlite3  # pylint: disable=import-outside-toplevel
        return sqlite3.connect(path)
