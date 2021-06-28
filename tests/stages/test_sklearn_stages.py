import numpy
import pandas
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from pdpcli.stages.sklearn_stages import SklearnPredictor, SklearnTransformer


def test_sklearn_predictor() -> None:
    df = pandas.DataFrame(
        data=numpy.random.normal(size=(64, 2)),
        columns=["a", "b"],
    )
    df["c"] = ((df["a"] + df["b"]) > 0).apply(int)

    stage = SklearnPredictor(
        estimator=LogisticRegression(),
        feature_columns=["a", "b"],
        target_columns="c",
        output_columns="d",
    )
    output = stage.apply(df)

    assert list(output.columns) == ["a", "b", "c", "d"]


def test_sklearn_predictor_without_feature_columns() -> None:
    df = pandas.DataFrame(
        data=numpy.random.normal(size=(64, 2)),
        columns=["a", "b"],
    )
    df["c"] = ((df["a"] + df["b"]) > 0).apply(int)

    stage = SklearnPredictor(
        estimator=LogisticRegression(),
        target_columns="c",
        output_columns="d",
    )
    output = stage.apply(df)

    assert list(output.columns) == ["a", "b", "c", "d"]


def test_sklearn_transformer_with_tfidf_vectorizer() -> None:
    df = pandas.DataFrame()
    df["text"] = ["This is a first sentence.", "This is a second sentence."]

    stage = SklearnTransformer(
        transformer=TfidfVectorizer(token_pattern=r"(?u)\b\w+\b"),
        feature_columns="text",
        output_columns="tfidf",
    )
    output = stage.apply(df)

    assert len(output.columns) == 6
    assert list(output.columns) == [
        "tfidf_a",
        "tfidf_first",
        "tfidf_is",
        "tfidf_second",
        "tfidf_sentence",
        "tfidf_this",
    ]


def test_sklearn_transformer_without_feature_columns() -> None:
    df = pandas.DataFrame(data=numpy.random.normal(size=(64, 32)))

    stage = SklearnTransformer(
        transformer=PCA(n_components=8),
        output_columns="pca",
    )
    output = stage.apply(df)

    assert len(output.columns) == 8
    assert list(output.columns) == [
        "pca_0",
        "pca_1",
        "pca_2",
        "pca_3",
        "pca_4",
        "pca_5",
        "pca_6",
        "pca_7",
    ]
