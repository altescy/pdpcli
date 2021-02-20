import argparse
import logging
import pickle
from pathlib import Path

import pdpipe  # pylint: disable=unused-import

from pdpcli import util
from pdpcli.builder import ConfigBuilder
from pdpcli.commands.subcommand import Subcommand
from pdpcli.exceptions import ConfigurationError

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
            "pipeline",
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
        config_reader = util.infer_config_reader(args.config)
        if config_reader is None:
            raise ConfigurationError("Failed to infer config reader.")

        config = config_reader.read(args.config, args.overrides)
        logger.info("Configurations:  %s", str(config))

        builder = ConfigBuilder.build(config)
        pipeline = builder.pipeline

        logger.info("Build pipeline:\n%s", str(pipeline))

        if args.input_file:
            reader = builder.reader or util.infer_data_reader(args.input_file)
            if reader is None:
                raise ConfigurationError("Failed to infer data reader.")

            df = reader.read(args.input_file)

            logger.info("Fit model with: %s", args.input_file)
            pipeline.fit(df)

        logger.info("Save pipeline to: %s", args.pipeline)
        with open(args.pipeline, "wb") as fp:
            pickle.dump(pipeline, fp)

        logger.info("Done")
