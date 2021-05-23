import hashlib
import inspect
import logging
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Any, Callable, Dict, Iterator, List, Optional, Tuple, Union
from urllib.parse import urlparse

import requests
from fs import open_fs
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

from pdpcli.settings import CACHE_DIRRECTORY

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


def get_parent_path_and_filename(file_path: str) -> Tuple[str, str]:
    splitted = str(file_path).rsplit("/", 1)
    if len(splitted) == 2:
        parent, name = splitted
    else:
        parent = "./"
        name = str(file_path)
    return parent, name


def cached_path(
    url_or_filename: Union[str, Path],
    cache_dir: Optional[Union[str, Path]] = None,
) -> Path:
    cache_dir = Path(cache_dir or CACHE_DIRRECTORY)

    os.makedirs(cache_dir, exist_ok=True)

    parsed = urlparse(str(url_or_filename))

    if parsed.scheme in ("", "file", "osfs"):
        return Path(parsed.path)

    cache_path = cache_dir / _get_cached_filename(url_or_filename)
    if cache_path.exists():
        logger.info("use cache for %s: %s", str(url_or_filename), str(cache_path))
        return cache_path

    cache_fp = open(cache_path, "w+b")
    try:
        with open_file(url_or_filename, "r+b") as fp:
            cache_fp.write(fp.read())
    except Exception:
        cache_fp.close()
        os.remove(cache_path)
        raise
    finally:
        cache_fp.close()

    return cache_path


@contextmanager
def open_file(
    file_path: Union[str, Path],
    mode: str = "r",
    **kwargs: Any,
) -> Iterator[IO[Any]]:
    parsed = urlparse(str(file_path))

    if parsed.scheme in ("http", "https"):
        url = str(file_path)
        with open_file_with_http(url, mode=mode) as fp:
            yield fp

    else:
        with open_file_with_fs(file_path, mode=mode, **kwargs) as fp:
            yield fp


@contextmanager
def open_file_with_http(
    url: str,
    mode: str = "r",
    **kwargs: Any,
) -> Iterator[IO[Any]]:
    if not mode.startswith("r"):
        raise ValueError(f"invalid mode for http(s): {mode}")
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        _http_get(url, temp_file)
        temp_file.close()
        with open(temp_file.name, mode, **kwargs) as fp:
            yield fp
    finally:
        os.remove(temp_file.name)


@contextmanager
def open_file_with_fs(
    file_path: Union[str, Path],
    *args: Any,
    **kwargs: Any,
) -> Iterator[IO[Any]]:
    file_path = str(file_path)
    parent, name = get_parent_path_and_filename(file_path)

    with open_fs(parent) as fs:
        with fs.open(name, *args, **kwargs) as fp:
            yield fp


def _session_with_backoff() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    return session


def _http_get(url: str, temp_file: IO[Any]) -> None:
    with _session_with_backoff() as session:
        req = session.get(url, stream=True)
        req.raise_for_status()
        content_length = req.headers.get("Content-Length")
        total = int(content_length) if content_length is not None else None
        progress = tqdm(unit="B", total=total, desc="downloading")
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                progress.update(len(chunk))
                temp_file.write(chunk)
        progress.close()


def _get_cached_filename(path: Union[str, Path]) -> str:
    encoded_path = str(path).encode()
    name = hashlib.md5(encoded_path).hexdigest()
    ext = get_file_ext(path)
    return name + ext
