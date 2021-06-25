import inspect
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def camel_to_snake(s: str) -> str:
    underscored = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", underscored).lower()


def get_args_list(func: Callable) -> List[str]:  # type: ignore
    signature = inspect.signature(func)
    return list(signature.parameters.keys())


def filter_kwargs(
    func: Callable,  # type: ignore
    kwargs: Dict[str, Any],
    ignored_args: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if ignored_args is None:
        ignored_args = ["self"]
    args = get_args_list(func)
    valid_kwargs = {
        key: value
        for key, value in kwargs.items()
        if key in args and key not in ignored_args
    }
    return valid_kwargs


def get_file_ext(file_path: Union[str, Path]) -> str:
    file_path = Path(file_path)
    return file_path.suffix
