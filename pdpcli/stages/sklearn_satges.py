import inspect

import pandas
from pdpipe.shared import _identity_function
from sklearn.feature_extraction.text import TfidfVectorizer

from pdpcli.stages import PdPipelineStage


def _get_args_list(func):
    signature = inspect.signature(func)
    return list(signature.parameters.keys())


@PdPipelineStage.register("tfidf_vectorize_token_lists", exist_ok=True)
class TfidfVectorizeTokenLists(PdPipelineStage):

    _DEF_CNTVEC_MSG = "Count-vectorizing column {}."

    def __init__(self, column, drop=True, hierarchical_labels=False, **kwargs):
        self._column = column
        self._drop = drop
        self._hierarchical_labels = hierarchical_labels
        msg = TfidfVectorizeTokenLists._DEF_CNTVEC_MSG.format(column)
        super_kwargs = {
            "exmsg": ("TfIdfVectorizeTokenLists precondition not met:"
                      f"{column} column not found."),
            "desc":
            msg,
        }
        valid_vectorizer_args = _get_args_list(TfidfVectorizer.__init__)
        self._vectorizer_args = {
            k: kwargs[k]
            for k in kwargs if k in valid_vectorizer_args and k not in [
                'input',
                'analyzer',
                'self',
            ]
        }
        pipeline_stage_args = {
            k: kwargs[k]
            for k in kwargs if k in PdPipelineStage._INIT_KWARGS
        }
        super_kwargs.update(**pipeline_stage_args)
        super().__init__(**super_kwargs)

        self._tfidf_vectorizer = TfidfVectorizer(
            input='content',
            analyzer=_identity_function,
            **self._vectorizer_args,
        )
        self._n_features = -1
        self._res_col_names = []

    def _prec(self, df):
        return self._column in df.columns

    def _fit_transform(self, df, verbose):
        vectorized = self._tfidf_vectorizer.fit_transform(df[self._column])
        self._n_features = vectorized.shape[1]

        if self._hierarchical_labels:
            self._res_col_names = [
                f'{self._column}_{f}'
                for f in self._tfidf_vectorizer.get_feature_names()
            ]
        else:
            self._res_col_names = self._tfidf_vectorizer.get_feature_names()

        vec_df = pandas.DataFrame.sparse.from_spmatrix(
            data=vectorized,
            index=df.index,
            columns=self._res_col_names,
        )
        inter_df = pandas.concat([df, vec_df], axis=1)

        self.is_fitted = True

        if self._drop:
            return inter_df.drop(self._column, axis=1)

        return inter_df

    def _transform(self, df, verbose):
        vectorized = self._tfidf_vectorizer.transform(df[self._column])

        vec_df = pandas.DataFrame.sparse.from_spmatrix(
            data=vectorized,
            index=df.index,
            columns=self._res_col_names,
        )
        inter_df = pandas.concat([df, vec_df], axis=1)

        if self._drop:
            return inter_df.drop(self._column, axis=1)

        return inter_df
