from typing import Any, Dict, List, Union

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader  # type: ignore


def load_yaml(yaml_string: str) -> Union[Dict[str, Any], List[Any]]:
    data: Union[Dict[str, Any], List[Any]] = load(
        yaml_string,
        Loader=Loader,
    )
    return data
