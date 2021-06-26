from typing import List, Union

import numpy
import pandas
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin

from pdpcli.stages.stage import Stage


@Stage.register("sklearn_predictor")
class SklearnPredictor(Stage):
    def __init__(
        self,
        estimator: BaseEstimator,
        feature_columns: Union[str, List[str]],
        target_columns: Union[str, List[str]],
        output_columns: Union[str, List[str]],
    ) -> None:
        super().__init__()
        self._estimator = estimator
        self._feature_columns = feature_columns
        self._target_columns = target_columns
        self._output_columns = output_columns

    def _prec(self, df: pandas.DataFrame) -> bool:
        feature_columns = self._feature_columns
        target_columns = self._target_columns
        if isinstance(feature_columns, str):
            feature_columns = [feature_columns]
        if isinstance(target_columns, str):
            target_columns = [target_columns]

        return set(feature_columns) <= set(df.columns) and set(target_columns) <= set(
            df.columns
        )

    def _fit_transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        X = df[self._feature_columns]
        y = df[self._target_columns]
        self._estimator.fit(X, y)
        self.is_fitted = True
        return self._transform(df, verbose)

    def _transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        X = df[self._feature_columns]
        output = self._estimator.predict(X)

        if output.ndim == 1:
            output = numpy.expand_dims(output, axis=1)  # type: ignore
        elif output.ndim > 2:
            raise RuntimeError(
                "# dim of prediction array must be less than or equal 2."
            )

        output_size = output.shape[-1]
        output_columns = self._output_columns
        if isinstance(output_columns, str):
            output_columns = [output_columns]

        if len(output_columns) == 1 and output_size > 1:
            col = output_columns[0]
            output_columns = [f"{col}_{i}" for i in range(output_size)]
        elif len(output_columns) != output_size:
            raise RuntimeError(
                f"Size of predictions must be equal to the length of output_columns."
                f"({len(self._output_columns)} != {output_size})"
            )

        if sparse.issparse(output):
            vec_df = pandas.DataFrame.sparse.from_spmatrix(
                data=output,
                index=df.index,
                columns=output_columns,
            )
        else:
            vec_df = pandas.DataFrame(
                data=output,
                index=df.index,
                columns=output_columns,
            )

        inter_df = pandas.concat([df, vec_df], axis=1)
        return inter_df


@Stage.register("sklearn_transformer")
class SklearnTransformer(Stage):
    def __init__(
        self,
        transformer: TransformerMixin,
        feature_columns: Union[str, List[str]],
        output_columns: Union[str, List[str]],
        drop: bool = True,
    ) -> None:
        super().__init__()
        self._transformer = transformer
        self._feature_columns = feature_columns
        self._output_columns = output_columns
        self._drop = drop

    def _prec(self, df: pandas.DataFrame) -> bool:
        feature_columns = self._feature_columns
        if isinstance(feature_columns, str):
            feature_columns = [feature_columns]
        return set(feature_columns) <= set(df.columns)

    def _fit_transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        X = df[self._feature_columns]
        self._transformer.fit(X)
        self.is_fitted = True
        return self._transform(df, verbose)

    def _transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        X = df[self._feature_columns]
        output = self._transformer.fit_transform(X)

        if output.ndim == 1:
            output = numpy.expand_dims(output, axis=1)  # type: ignore
        elif output.ndim > 2:
            raise RuntimeError(
                "# dim of transformed array must be less than or equal 2."
            )

        output_size = output.shape[-1]
        output_columns = self._output_columns
        if isinstance(output_columns, str):
            output_columns = [output_columns]

        if len(output_columns) == 1:
            col = output_columns[0]
            if hasattr(self._transformer, "get_feature_names"):
                output_columns = [
                    f"{col}_{name}" for name in self._transformer.get_feature_names()
                ]
            elif output_size > 1:
                output_columns = [f"{col}_{i}" for i in range(output_size)]
            else:
                output_columns = output_columns
        else:
            output_columns = output_columns

        if len(output_columns) != output_size:
            raise RuntimeError(
                f"Size of transformed array must be equal to the length of output_columns."
                f"({len(self._output_columns)} != {output_size})"
            )

        if sparse.issparse(output):
            vec_df = pandas.DataFrame.sparse.from_spmatrix(
                data=output,
                index=df.index,
                columns=output_columns,
            )
        else:
            vec_df = pandas.DataFrame(
                data=output,
                index=df.index,
                columns=output_columns,
            )

        inter_df = pandas.concat([df, vec_df], axis=1)

        if self._drop:
            inter_df = inter_df.drop(self._feature_columns, axis=1)

        return inter_df
