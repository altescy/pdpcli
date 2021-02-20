from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import logging

from omegaconf import OmegaConf, DictConfig, ListConfig

from pdpcli.exceptions import ConfigurationError
from pdpcli.filetype import FileType
from pdpcli.configs.jsonnet import load_jsonnet
from pdpcli.configs.yaml import load_yaml

logger = logging.getLogger(__name__)


def load_config_file(
    file_path: Path,
    args: Optional[List[str]] = None,
):
    filetype = FileType.from_path(file_path)

    args_config = load_omegaconf_from_args(args or [])

    if filetype == FileType.YAML:
        config = load_omegaconf_from_yaml(file_path)
    elif filetype == FileType.JSON:
        config = load_omegaconf_from_json(file_path)
    elif filetype == FileType.JSONNET:
        config = load_omegaconf_from_jsonnet(file_path)
    else:
        raise ConfigurationError(f"Unsupported config file type: {file_path}")

    if isinstance(config, DictConfig) and args:
        config = OmegaConf.merge(config, args_config)
    elif args:
        logger.warning("command line configs are ignored because "
                       "the file config is not a DictConfig")

    config_yaml = OmegaConf.to_yaml(config)
    return load_yaml(config_yaml)


def load_omegaconf_from_yaml(file_path: Path) -> Union[DictConfig, ListConfig]:
    return OmegaConf.load(file_path)


def load_omegaconf_from_json(file_path: Path) -> Union[DictConfig, ListConfig]:
    with open(file_path, "r") as fp:
        jsondict = json.load(fp)
    return OmegaConf.create(jsondict)  # type: ignore


def load_omegaconf_from_jsonnet(
        file_path: Path) -> Union[DictConfig, ListConfig]:
    jsondict = load_jsonnet(file_path)
    return OmegaConf.create(jsondict)


def load_omegaconf_from_args(args: List[str]) -> Union[DictConfig, ListConfig]:
    return OmegaConf.from_dotlist(args)
