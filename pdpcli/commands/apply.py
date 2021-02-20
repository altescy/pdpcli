import argparse
import logging
import pickle
import sys
from pathlib import Path

import pdpipe

from pdpcli.build import build_pdpipe
from pdpcli.commands.subcommand import Subcommand
from pdpcli.configs import load_config_file
from pdpcli.data import load_dataframe_from_file
from pdpcli.filetype import FileType
from pdpcli.settings import DEFAULT_COLT_SETTING

logger = logging.getLogger(__name__)


@Subcommand.register(
    "apply",
    description="Apply pipelines to given data",
    help="Apply pipelines to given data",
)
class ApplyCommand(Subcommand):
    def set_arguments(self) -> None:
        self.parser.add_argument(
            "model",
            type=Path,
            help="path to trained model or config file",
        )
        self.parser.add_argument(
            "input_file",
            type=Path,
            help="path to a input file to apply pipeline",
        )
        self.parser.add_argument(
            "-o",
            "--output_file",
            type=Path,
            help="path to a output file of result data frame",
        )
        self.parser.add_argument(
            "overrides",
            nargs="*",
            help="arguments to override config values",
        )
        self.parser.add_argument(
            "--quiet",
            action="store_true",
            help="do not show result dataframe to stdout",
        )

    def run(self, args: argparse.Namespace) -> None:
        logger.info("Load model from: %s", str(args.model))
        model = self._load_model(args.model)

        logger.info("Model:\n%s", str(model))

        logger.info("Load input file: %s", str(args.input_file))
        df = load_dataframe_from_file(args.input_file)

        logger.info("Apply pipeline")
        result_df = model.apply(df)

        if args.output_file:
            result_df.to_csv(args.output_file, index=False)

        if not args.quiet:
            result_df.to_csv(sys.stdout, index=False)

        logger.info("Done")

    @staticmethod
    def _load_model(file_path: Path) -> pdpipe.PdPipelineStage:
        filetype = FileType.from_path(file_path)
        if filetype == FileType.PICKLE:
            with open(file_path, "rb") as fp:
                model = pickle.load(fp)
        else:
            config = load_config_file(file_path)
            model = build_pdpipe(config, **DEFAULT_COLT_SETTING)
        return model
