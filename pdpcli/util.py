from typing import Any, IO, Iterator
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from urllib.parse import urlparse
import re
import tempfile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fs import open_fs
from tqdm import tqdm


def camel_to_snake(s: str) -> str:
    underscored = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', underscored).lower()


@contextmanager
def open_file(file_path: PathLike,
              mode: str = "r",
              **kwargs) -> Iterator[IO[Any]]:
    parsed = urlparse(str(file_path))

    if parsed.scheme in ("http", "https"):

        if not mode.startswith("r"):
            raise ValueError(f"invalid mode for http(s): {mode}")

        url = str(file_path)
        with tempfile.TemporaryFile(mode=mode) as fp:
            _http_get(url, fp)
            yield fp

    else:

        with open_file_with_fs(file_path, **kwargs) as fp:
            yield fp


@contextmanager
def open_file_with_fs(file_path: PathLike, *args,
                      **kwargs) -> Iterator[IO[Any]]:
    file_path = Path(file_path)
    parent = str(file_path.parent)
    name = str(file_path.name)

    with open_fs(parent) as fs:
        with fs.open(name, *args, **kwargs) as fp:
            yield fp


def _session_with_backoff() -> requests.Session:
    """
    https://stackoverflow.com/questions/23267409/how-to-implement-retry-mechanism-into-python-requests-library
    """
    session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=1,
                    status_forcelist=[502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    return session


def _http_get(url: str, temp_file: IO) -> None:
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
