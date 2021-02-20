from pathlib import Path

import pandas

from pdpcli.filetype import FileType


def load_dataframe_from_file(file_path: Path) -> pandas.DataFrame:
    filetype = FileType.from_path(file_path)

    if filetype == FileType.CSV:
        return pandas.read_csv(file_path)

    if filetype == FileType.TSV:
        return pandas.read_csv(file_path, sep="\t")

    if filetype == FileType.JSONL:
        return pandas.read_json(file_path, orient="records")

    if filetype == FileType.PICKLE:
        return pandas.read_pickle(file_path)

    raise RuntimeError(f"Invalid file type: {file_path}")
