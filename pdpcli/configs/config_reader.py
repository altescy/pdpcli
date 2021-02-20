from typing import cast, Any, Dict, List, Union
from pathlib import Path
import json
import logging

import colt
from omegaconf import OmegaConf, DictConfig, ListConfig

from pdpcli.configs.yaml import load_yaml
from pdpcli.configs.jsonnet import load_jsonnet

logger = logging.getLogger(__name__)


class ConfigReader(colt.Registrable):
    def read(
        self,
        file_path: Path,
        overrides: List[str] = None,
    ) -> Dict[str, Any]:
        config = self._read(file_path)

        assert isinstance(config, DictConfig), "config should be a dict"

        if overrides:
            args_config = OmegaConf.from_dotlist(overrides)
            config = OmegaConf.merge(config, args_config)

        config_yaml = OmegaConf.to_yaml(config)
        return cast(Dict[str, Any], load_yaml(config_yaml))

    def _read(self, file_path: Path) -> Union[DictConfig, ListConfig]:
        raise NotImplementedError


@ConfigReader.register("yaml")
class YamlConfigReader(ConfigReader):
    def _read(self, file_path: Path) -> Union[DictConfig, ListConfig]:
        return OmegaConf.load(file_path)


@ConfigReader.register("json")
class JsonConfigReader(ConfigReader):
    def _read(self, file_path: Path) -> Union[DictConfig, ListConfig]:
        with open(file_path, "r") as fp:
            jsondict = json.load(fp)
        return OmegaConf.create(jsondict)  # type: ignore


@ConfigReader.register("jsonnet")
class JsonnetConfigReader(ConfigReader):
    def _read(self, file_path: Path) -> Union[DictConfig, ListConfig]:
        jsondict = load_jsonnet(file_path)
        return OmegaConf.create(jsondict)
