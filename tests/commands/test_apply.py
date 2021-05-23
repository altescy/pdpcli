import tempfile
from pathlib import Path

import pandas

from pdpcli.commands import create_parser
from pdpcli.commands.apply import ApplyCommand


def test_apply_from_config():
    fixture_path = Path("tests/fixture")
    config_path = fixture_path / "configs" / "config.yml"
    input_file = fixture_path / "data" / "data.csv"

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        output_file = tempdir / "output.csv"

        parser = create_parser()
        args = parser.parse_args(
            [
                "apply",
                str(config_path),
                str(input_file),
                "-o",
                str(output_file),
            ]
        )

        args.func(args)

        assert output_file.is_file()

        input_df = pandas.read_csv(input_file)
        output_df = pandas.read_csv(output_file)

        assert len(input_df) == len(output_df)
        assert "name" not in output_df.columns
        assert "job" not in output_df.columns


def test_apply_from_pickled_model():
    fixture_path = Path("tests/fixture")
    pipeline_path = fixture_path / "data" / "pipeline.pkl"
    input_file = fixture_path / "data" / "data.csv"

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        output_file = tempdir / "output.csv"

        parser = create_parser()
        args = parser.parse_args(
            [
                "apply",
                str(pipeline_path),
                str(input_file),
                "-o",
                str(output_file),
            ]
        )

        args.func(args)

        assert output_file.is_file()

        input_df = pandas.read_csv(input_file)
        output_df = pandas.read_csv(output_file)

        assert len(input_df) == len(output_df)
        assert "name" not in output_df.columns
        assert "job" not in output_df.columns


def test_apply_with_cli_args():
    fixture_path = Path("tests/fixture")
    config_path = fixture_path / "configs" / "config.yml"
    input_file = fixture_path / "data" / "data.csv"

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        output_file = tempdir / "output.csv"

        parser = create_parser()
        args = parser.parse_args(
            [
                "apply",
                str(config_path),
                str(input_file),
                "pipeline.stages.drop_columns.columns=[name]",
                "-o",
                str(output_file),
            ]
        )

        args.func(args)

        assert output_file.is_file()

        input_df = pandas.read_csv(input_file)
        output_df = pandas.read_csv(output_file)

        assert len(input_df) == len(output_df)
        assert "name" not in output_df.columns
        assert "job" in output_df.columns
