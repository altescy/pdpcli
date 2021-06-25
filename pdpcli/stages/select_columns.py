import re
from typing import Any, List, Union

import pandas

from pdpcli.stages.stage import Stage


@Stage.register("select_columns")
class SelectColumns(Stage):
    def __init__(self, columns: Union[str, List[str]], **kwargs: Any) -> None:
        if isinstance(columns, str):
            columns = [columns]

        super().__init__(**kwargs)
        self._columns = columns

    def _prec(self, df: pandas.DataFrame) -> bool:
        return True

    def _transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        return df[self._columns]


@Stage.register("rex_columns")
class RexColumns(Stage):
    def __init__(self, columns: Union[str, List[str]], **kwargs: Any) -> None:
        if isinstance(columns, str):
            columns = [columns]

        super().__init__(**kwargs)
        self._columns = [re.compile(c) for c in columns]

    def _prec(self, df: pandas.DataFrame) -> bool:
        return True

    def _transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        columns = [c for c in df.columns if any(re.match(r, c) for r in self._columns)]
        return df[columns]
