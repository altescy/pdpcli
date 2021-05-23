import tempfile
from pathlib import Path

from pdpcli.commands import create_parser
from pdpcli.commands.build import BuildCommand


def test_build_without_input_file():
    fixture_path = Path("tests/fixture")
    config_path = fixture_path / "configs" / "config.yml"

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        pipeline_path = tempdir / "pipeline.pkl"

        parser = create_parser()
        args = parser.parse_args(
            [
                "build",
                str(config_path),
                str(pipeline_path),
            ]
        )

        args.func(args)

        assert pipeline_path.is_file()


def test_build_with_input_file():
    fixture_path = Path("tests/fixture")
    config_path = fixture_path / "configs" / "config.yml"
    input_file = fixture_path / "data" / "data.csv"

    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = Path(tempdir)
        pipeline_path = tempdir / "pipeline.pkl"

        parser = create_parser()
        args = parser.parse_args(
            [
                "build",
                str(config_path),
                str(pipeline_path),
                "-i",
                str(input_file),
            ]
        )

        args.func(args)

        assert pipeline_path.is_file()
