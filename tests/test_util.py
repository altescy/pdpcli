import tempfile
from pathlib import Path

from pdpcli import util


def test_camel_to_snake():
    text = "ThisIsTestText"
    processed = util.camel_to_snake(text)
    assert processed == "this_is_test_text"


def test_get_args_list():
    def func(a, b):
        return a, b

    args = util.get_args_list(func)
    assert args == ["a", "b"]
