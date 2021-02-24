import pandas

from pdpcli.stages.pass_through_stage import PassThroughStage


def _generate_dataframe():
    df = pandas.DataFrame()
    df["name"] = ["foo", "bar", "baz"]
    df["age"] = [10, 20, 30]
    return df


def test_pass_through_stage():
    df = _generate_dataframe()
    stage = PassThroughStage()
    processed_df = stage.apply(df)

    assert processed_df["name"].to_list() == ["foo", "bar", "baz"]
    assert processed_df["age"].to_list() == [10, 20, 30]
