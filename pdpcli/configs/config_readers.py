from typing import cast, Any, Dict, List, Union
from pathlib import Path
import json
import logging

from omegaconf import OmegaConf, DictConfig, ListConfig

from pdpcli import util
from pdpcli.registrable import RegistrableWithFile
from pdpcli.configs.jsonnet import load_jsonnet

logger = logging.getLogger(__name__)


class ConfigReader(RegistrableWithFile):
    def read(
        self,
        file_path: Union[str, Path],
        overrides: List[str] = None,
    ) -> Union[Dict[str, Any]]:
        config = self._read(file_path)

        assert isinstance(config, DictConfig), "config should be a dict"

        if overrides:
            args_config = OmegaConf.from_dotlist(overrides)
            config = OmegaConf.merge(config, args_config)

        container = OmegaConf.to_container(config, resolve=True)
        return cast(Dict[str, Any], container)

    def _read(
        self,
        file_path: Union[str, Path],
    ) -> Union[DictConfig, ListConfig]:
        raise NotImplementedError


@ConfigReader.register("yaml", extensions=[".yml", ".yaml"])
class YamlConfigReader(ConfigReader):
    def _read(
        self,
        file_path: Union[str, Path],
    ) -> Union[DictConfig, ListConfig]:
        file_path = util.cached_path(file_path)
        return OmegaConf.load(file_path)


@ConfigReader.register("json", extensions=[".json"])
class JsonConfigReader(ConfigReader):
    def _read(
        self,
        file_path: Union[str, Path],
    ) -> Union[DictConfig, ListConfig]:
        file_path = util.cached_path(file_path)
        with open(file_path, "r") as fp:
            jsondict = json.load(fp)
        return OmegaConf.create(jsondict)  # type: ignore


@ConfigReader.register("jsonnet", extensions=[".jsonnet"])
class JsonnetConfigReader(ConfigReader):
    def _read(
        self,
        file_path: Union[str, Path],
    ) -> Union[DictConfig, ListConfig]:
        file_path = util.cached_path(file_path)
        jsondict = load_jsonnet(file_path)
        return OmegaConf.create(jsondict)
