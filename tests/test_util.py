import tempfile

from pdpcli import util


def test_camel_to_snake():
    text = "ThisIsTestText"
    processed = util.camel_to_snake(text)
    assert processed == "this_is_test_text"


def test_cached_path():
    url = "https://github.com/altescy/pdpcli/raw/main/tests/fixture/data/data.csv"

    with tempfile.TemporaryDirectory() as cache_dir:
        file_path = util.cached_path(url, cache_dir=cache_dir)
        assert file_path.is_file()
