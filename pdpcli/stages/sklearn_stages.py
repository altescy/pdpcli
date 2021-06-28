from typing import Any, List, Optional, Tuple, Union

import numpy
import pandas
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin

from pdpcli.stages.stage import Stage


@Stage.register("sklearn_predictor")
class SklearnPredictor(Stage):
    _DEF_SKLEARN_PREDICTOR_DESC = "SklearnPredictor with {} feature {}, target {}"

    def __init__(
        self,
        estimator: BaseEstimator,
        target_columns: Union[str, List[str]],
        output_columns: Union[str, List[str]],
        feature_columns: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> None:
        desc = SklearnPredictor._DEF_SKLEARN_PREDICTOR_DESC.format(
            type(estimator).__name__,
            feature_columns or "ALL COLUMNS",
            target_columns,
        )
        super_kwargs = {
            "desc": desc,
        }
        super_kwargs.update(**kwargs)
        super().__init__(**super_kwargs)
        self._estimator = estimator
        self._feature_columns = feature_columns
        self._target_columns = target_columns
        self._output_columns = output_columns

    def _prec(self, df: pandas.DataFrame) -> bool:
        target_columns = self._target_columns
        if isinstance(target_columns, str):
            target_columns = [target_columns]

        condition = set(target_columns) <= set(df.columns)

        if self._feature_columns is not None:
            feature_columns = self._feature_columns
            if isinstance(feature_columns, str):
                feature_columns = [feature_columns]

            condition = condition and set(feature_columns) <= set(df.columns)

        return condition

    def _get_X_y(
        self,
        df: pandas.DataFrame,
        return_y: bool = True,
    ) -> Tuple[
        Union[pandas.DataFrame, pandas.Series],
        Optional[Union[pandas.DataFrame, pandas.Series]],
    ]:
        if self._feature_columns:
            feature_columns = self._feature_columns
        else:
            target_columns = self._target_columns
            if isinstance(target_columns, str):
                target_columns = [target_columns]

            feature_columns = list(set(df.columns) - set(target_columns))

        X = df[feature_columns]
        y = df[self._target_columns] if return_y else None
        return X, y

    def _fit_transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        X, y = self._get_X_y(df)
        self._estimator.fit(X, y)
        self.is_fitted = True
        return self._transform(df, verbose)

    def _transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        X, _ = self._get_X_y(df, return_y=False)
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
    _DEF_SKLEARN_TRANSFORMER_DESC = "Sklearn transofmer with {} column {}."

    def __init__(
        self,
        transformer: TransformerMixin,
        output_columns: Union[str, List[str]],
        feature_columns: Optional[Union[str, List[str]]] = None,
        drop: bool = True,
        **kwargs: Any,
    ) -> None:
        desc = SklearnTransformer._DEF_SKLEARN_TRANSFORMER_DESC.format(
            type(transformer).__name__,
            feature_columns or "ALL COLUMNS",
        )
        super_kwargs = {
            "desc": desc,
        }
        super_kwargs.update(**kwargs)
        super().__init__(**super_kwargs)
        self._transformer = transformer
        self._feature_columns = feature_columns
        self._output_columns = output_columns
        self._drop = drop

    def _prec(self, df: pandas.DataFrame) -> bool:
        if self._feature_columns is None:
            return True
        feature_columns = self._feature_columns
        if isinstance(feature_columns, str):
            feature_columns = [feature_columns]
        return set(feature_columns) <= set(df.columns)

    def _fit_transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        X = df[self._feature_columns] if self._feature_columns else df
        self._transformer.fit(X)
        self.is_fitted = True
        return self._transform(df, verbose)

    def _transform(self, df: pandas.DataFrame, verbose: bool) -> pandas.DataFrame:
        if self._feature_columns:
            feature_columns = self._feature_columns
        else:
            feature_columns = list(df.columns)

        X = df[feature_columns]
        output = self._transformer.transform(X)

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
            inter_df = inter_df.drop(feature_columns, axis=1)

        return inter_df
