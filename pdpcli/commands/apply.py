import argparse
import logging
import pickle
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union

import minato
import pdpipe

from pdpcli import util
from pdpcli.commands.subcommand import Subcommand
from pdpcli.configs import ConfigBuilder, ConfigReader
from pdpcli.data import DataReader, DataWriter
from pdpcli.exceptions import ConfigurationError

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
            type=str,
            help="path to trained model or config file",
        )
        self.parser.add_argument(
            "input_file",
            type=str,
            help="path to a input file to apply pipeline",
        )
        self.parser.add_argument(
            "-o",
            "--output-file",
            type=str,
            help="path to a output file of result data frame",
        )
        self.parser.add_argument(
            "-c",
            "--config",
            type=str,
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
            help="do not show result dataframe on stdout",
        )

    def run(self, args: argparse.Namespace) -> None:
        # Load pipeline
        logger.info("Load pipeline from: %s", str(args.pipeline))
        if self._is_pickle_file(args.pipeline):
            pipeline = self._load_pipeline_from_pickle(args.pipeline)
            reader, writer = None, None
        else:
            pipeline, reader, writer = self._build_config(args.pipeline, args.overrides)

        logger.info("Pipeline:\n%s", str(pipeline))

        # Construct reader / writer from config
        if args.config:
            logger.info("Load data reader / writer from: %s", str(args.config))
            _, reader, writer = self._build_config(args.config, args.overrides)

        # Read input file
        reader = reader or DataReader.from_path(args.input_file)
        if reader is None:
            raise ConfigurationError("Failed to infer data reader")
        logger.info("Load input file: %s", str(args.input_file))
        df = reader.read(args.input_file)

        # Apply pipeline
        logger.info("Apply pipeline")
        result_df = pipeline.apply(df)

        # Save processed data
        if args.output_file:
            writer = writer or DataWriter.from_path(args.output_file)
            if writer is None:
                raise ConfigurationError("Failed to infer data writer.")

            logger.info("Writer result data frame: %s", str(args.output_file))
            writer.write(result_df, args.output_file)

        if not args.quiet:
            result_df.to_csv(sys.stdout, index=False)

        logger.info("Done")

    @staticmethod
    def _is_pickle_file(file_path: Union[str, Path]) -> bool:
        ext = util.get_file_ext(file_path)
        return ext in (".pkl", ".pickle")

    @staticmethod
    def _load_pipeline_from_pickle(
        file_path: Union[str, Path]
    ) -> pdpipe.PdPipelineStage:
        file_path = minato.cached_path(file_path)
        with minato.open(file_path, "rb") as fp:
            pipeline = pickle.load(fp)
        return pipeline

    @staticmethod
    def _build_config(
        file_path: Union[str, Path],
        overrides: Optional[List[str]] = None,
    ) -> Tuple[pdpipe.PdPipelineStage, Optional[DataReader], Optional[DataWriter]]:
        config_reader = ConfigReader.from_path(file_path)
        if config_reader is None:
            raise ConfigurationError("Failed to infer config reader.")

        config = config_reader.read(file_path, overrides)
        logger.info("Load config: %s", str(config))

        builder = ConfigBuilder.build(config)
        pipeline = builder.pipeline
        reader = builder.reader
        writer = builder.writer

        return pipeline, reader, writer
