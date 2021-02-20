import argparse
import logging
import pickle
from pathlib import Path

import pdpipe

from pdpcli.build import build_pdpipe
from pdpcli.commands.subcommand import Subcommand
from pdpcli.configs import load_config_file
from pdpcli.data import load_dataframe_from_file
from pdpcli.settings import DEFAULT_COLT_SETTING

logger = logging.getLogger(__name__)


@Subcommand.register(
    "build",
    description="Build a PdPipe model from a configuration file",
    help="Build a PdPipe model from a configuration file",
)
class BuildCommand(Subcommand):
    def set_arguments(self) -> None:
        self.parser.add_argument(
            "config",
            type=Path,
            help="path to a configuration file",
        )
        self.parser.add_argument(
            "model",
            type=Path,
            help="path to a output file of a trained model",
        )
        self.parser.add_argument(
            "-i",
            "--input-file",
            type=Path,
            default=None,
            help="path to a input file for training",
        )
        self.parser.add_argument(
            "overrides",
            nargs="*",
            help="arguments to override config values",
        )

    def run(self, args: argparse.Namespace) -> None:
        config = load_config_file(args.config, args.overrides)
        logger.info("Configurations:  %s", str(config))

        model = build_pdpipe(
            config, **DEFAULT_COLT_SETTING)  # type: pdpipe.PdpipelineStage
        logger.info("Build model:\n%s", str(model))

        if args.input_file:
            logger.info("Fit model with: %s", args.input_file)
            df = load_dataframe_from_file(args.input_file)
            model.fit(df)

        logger.info("Save model to: %s", args.model)
        with open(args.model, "wb") as fp:
            pickle.dump(model, fp)

        logger.info("Done")
