import argparse
import logging
import pickle
import sys
from pathlib import Path
from typing import List

import pdpipe

from pdpcli import util
from pdpcli.builder import ConfigBuilder
from pdpcli.exceptions import ConfigurationError
from pdpcli.commands.subcommand import Subcommand
from pdpcli.filetype import FileType

logger = logging.getLogger(__name__)


@Subcommand.register(
    "apply",
    description="Apply pipelines to given data",
    help="Apply pipelines to given data",
)
class ApplyCommand(Subcommand):
    def set_arguments(self) -> None:
        self.parser.add_argument(
            "pipeline",
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
            "-c",
            "--config",
            type=Path,
            default=None,
            help="path to a output file for data reader / writer",
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
        logger.info("Load model from: %s", str(args.pipeline))
        pipeline = self._load_pipeline(args.pipeline, args.overrides)

        logger.info("Pipeline:\n%s", str(pipeline))

        reader = util.infer_data_reader(args.input_file)
        if reader is None:
            raise ConfigurationError("Failed to infer data reader")

        logger.info("Load input file: %s", str(args.input_file))
        df = reader.read(args.input_file)

        logger.info("Apply pipeline")
        result_df = pipeline.apply(df)

        if args.output_file:
            writer = util.infer_data_writer(args.output_file)
            if writer is None:
                raise ConfigurationError("Failed to infer data writer.")

            logger.info("Writer result data frame: %s", str(args.output_file))
            writer.write(result_df, args.output_file)

        if not args.quiet:
            result_df.to_csv(sys.stdout, index=False)

        logger.info("Done")

    @staticmethod
    def _load_pipeline(
        file_path: Path,
        overrides: List[str] = None,
    ) -> pdpipe.PdPipelineStage:
        filetype = FileType.from_path(file_path)
        if filetype == FileType.PICKLE:
            with open(file_path, "rb") as fp:
                pipeline = pickle.load(fp)
        else:
            config_reader = util.infer_config_reader(file_path)
            if config_reader is None:
                raise ConfigurationError("Failed to infer config reader.")

            config = config_reader.read(file_path, overrides)
            logger.info("Load config: %s", str(config))

            builder = ConfigBuilder.build(config)
            pipeline = builder.pipeline

        return pipeline
