import pandas

from pdpcli.stages.select_columns import SelectColumns


def test_select_columns() -> None:
    df = pandas.DataFrame()
    df["col_1"] = ["foo", "bar", "baz"]
    df["col_2"] = [10, 20, 30]
    df["xyz"] = ["a", "b", "c"]

    stage = SelectColumns(r"col_\d+")
    output = stage.apply(df)

    assert sorted(output.columns) == ["col_1", "col_2"]
