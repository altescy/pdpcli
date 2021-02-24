from pathlib import Path
import os
import tempfile
import sqlite3

import pandas

from pdpcli.data.data_writers import (
    CsvDataWriter,
    TsvDataWriter,
    JsonLinesDataWriter,
    PickleDataWriter,
    SqlDataWriter,
)


def _generate_dataframe():
    df = pandas.DataFrame()
    df["name"] = ["foo", "bar", "baz"]
    df["age"] = [10, 20, 30]
    return df


def test_csv_data_reader():
    df = _generate_dataframe()
    writer = CsvDataWriter()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        writer.write(df, temp_file.name)

    assert os.path.isfile(temp_file.name)

    exported_df = pandas.read_csv(temp_file.name)
    assert "name" in exported_df.columns
    assert "age" in exported_df.columns

    os.remove(temp_file.name)


def test_tsv_data_reader():
    df = _generate_dataframe()
    writer = TsvDataWriter()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        writer.write(df, temp_file.name)

    assert os.path.isfile(temp_file.name)

    exported_df = pandas.read_csv(temp_file.name, sep="\t")
    assert "name" in exported_df.columns
    assert "age" in exported_df.columns

    os.remove(temp_file.name)


def test_jsonl_data_reader():
    df = _generate_dataframe()
    writer = JsonLinesDataWriter()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        writer.write(df, temp_file.name)

    assert os.path.isfile(temp_file.name)

    exported_df = pandas.read_json(temp_file.name,
                                   orient="records",
                                   lines=True)
    assert "name" in exported_df.columns
    assert "age" in exported_df.columns

    os.remove(temp_file.name)


def test_pickle_data_reader():
    df = _generate_dataframe()
    writer = PickleDataWriter()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        writer.write(df, temp_file.name)

    assert os.path.isfile(temp_file.name)

    exported_df = pandas.read_pickle(temp_file.name)
    assert "name" in exported_df.columns
    assert "age" in exported_df.columns

    os.remove(temp_file.name)


def test_sql_data_reader():
    df = _generate_dataframe()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        dsn = f"sqlite:////{temp_file.name}"
        writer = SqlDataWriter(dsn=dsn)
        writer.write(df, "test_table")

    assert os.path.isfile(temp_file.name)

    query = "select * from test_table"
    with sqlite3.connect(temp_file.name) as con:
        exported_df = pandas.read_sql(query, con=con)
    assert "name" in exported_df.columns
    assert "age" in exported_df.columns

    os.remove(temp_file.name)
