from pathlib import Path

from pdpcli.configs.config_readers import (
    YamlConfigReader,
    JsonConfigReader,
    JsonnetConfigReader,
)

FIXTURE_PATH = Path("tests/fixture")


def test_yaml_config_reader():
    config_path = FIXTURE_PATH / "configs" / "config.yml"
    reader = YamlConfigReader()
    config = reader.read(config_path)
    assert isinstance(config, dict)


def test_json_config_reader():
    config_path = FIXTURE_PATH / "configs" / "config.json"
    reader = JsonConfigReader()
    config = reader.read(config_path)
    assert isinstance(config, dict)


def test_jsonnet_config_reader():
    config_path = FIXTURE_PATH / "configs" / "config.jsonnet"
    reader = JsonnetConfigReader()
    config = reader.read(config_path)
    assert isinstance(config, dict)
