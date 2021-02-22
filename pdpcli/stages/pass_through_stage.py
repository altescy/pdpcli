import pandas

from pdpcli.stages.stage import Stage


@Stage.register("pass_through")
class PassThroughStage(Stage):
    def _prec(self, df):
        return True

    def _transform(self, df: pandas.DataFrame, verbose: bool = False):
        return df
