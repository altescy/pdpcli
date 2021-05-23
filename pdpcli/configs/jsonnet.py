import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)

try:
    from _jsonnet import evaluate_file
except ImportError:

    def evaluate_file(filename: str, **_kwargs: Any) -> str:
        logger.warning("jsonnet is unavailable, treating %{filename}s as plain json")
        with open(filename, "r") as evaluation_file:
            return evaluation_file.read()


def _is_encodable(value: str) -> bool:
    return (value == "") or (value.encode("utf-8", "ignore") != b"")


def _environment_variables() -> Dict[str, str]:
    return {key: value for key, value in os.environ.items() if _is_encodable(value)}


def load_jsonnet(file_path: Union[Path, str]) -> Dict[str, Any]:
    ext_vars = _environment_variables()
    jsondict = json.loads(
        evaluate_file(str(file_path), ext_vars=ext_vars)
    )  # type: Dict[str, Any]
    return jsondict
