from pathlib import Path

import pandas

from pdpcli.data.data_readers import (
    CsvDataReader,
    JsonLinesDataReader,
    PickleDataReader,
    SqlDataReader,
    TsvDataReader,
)

FIXTURE_DIR = Path("./tests/fixture/")


def test_csv_data_reader():
    input_file = FIXTURE_DIR / "data" / "data.csv"
    reader = CsvDataReader()
    df = reader.read(input_file)

    assert isinstance(df, pandas.DataFrame)


def test_tsv_data_reader():
    input_file = FIXTURE_DIR / "data" / "data.tsv"
    reader = TsvDataReader()
    df = reader.read(input_file)

    assert isinstance(df, pandas.DataFrame)


def test_jsonl_data_reader():
    input_file = FIXTURE_DIR / "data" / "data.jsonl"
    reader = JsonLinesDataReader()
    df = reader.read(input_file)

    assert isinstance(df, pandas.DataFrame)


def test_pickle_data_reader():
    input_file = FIXTURE_DIR / "data" / "data.pkl"
    reader = PickleDataReader()
    df = reader.read(input_file)

    assert isinstance(df, pandas.DataFrame)


def test_sql_data_reader():
    input_file = FIXTURE_DIR / "data" / "query.sql"
    dsn = "sqlite:///tests/fixture/data/data.db"
    reader = SqlDataReader(dsn=dsn)
    df = reader.read(input_file)

    assert isinstance(df, pandas.DataFrame)
