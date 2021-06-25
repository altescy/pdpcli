import pandas

from pdpcli.stages.select_columns import RexColumns, SelectColumns


def test_select_columns() -> None:
    df = pandas.DataFrame()
    df["foo"] = ["foo", "bar", "baz"]
    df["bar"] = [10, 20, 30]
    df["baz"] = ["a", "b", "c"]

    stage = SelectColumns(["foo", "baz"])
    output = stage.apply(df)

    assert list(output.columns) == ["foo", "baz"]


def test_rex_columns() -> None:
    df = pandas.DataFrame()
    df["col_1"] = ["foo", "bar", "baz"]
    df["col_2"] = [10, 20, 30]
    df["xyz"] = ["a", "b", "c"]

    stage = RexColumns(r"col_\d+")
    output = stage.apply(df)

    assert sorted(output.columns) == ["col_1", "col_2"]
