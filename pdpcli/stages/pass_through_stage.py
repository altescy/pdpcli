from typing import Any

import pandas

from pdpcli.stages.stage import Stage


@Stage.register("pass_through")
class PassThroughStage(Stage):
    def __init__(self, **kwargs: Any) -> None:
        super_kwargs = {
            "desc": "Pass through stage.",
        }
        super_kwargs.update(**kwargs)
        super().__init__(**super_kwargs)

    def _prec(self, df: pandas.DataFrame) -> bool:
        return True

    def _transform(
        self,
        df: pandas.DataFrame,
        verbose: bool = False,
    ) -> pandas.DataFrame:
        return df
