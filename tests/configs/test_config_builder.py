from pdpcli.configs.config_builder import ConfigBuilder
from pdpcli.data import DataReader, DataWriter
from pdpcli.stages import Stage


def test_config_builder():
    config = {
        "colt": {"typekey": "!"},
        "reader": {
            "!": "csv",
        },
        "writer": {
            "!": "jsonl",
        },
        "pipeline": {
            "!": "pass_through",
        },
    }

    builder = ConfigBuilder.build(config)
    assert isinstance(builder.reader, DataReader)
    assert isinstance(builder.writer, DataWriter)
    assert isinstance(builder.pipeline, Stage)
