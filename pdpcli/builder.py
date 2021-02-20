from __future__ import annotations
from typing import cast, Any, Dict, Optional
import copy

import colt

from pdpcli.stages import PdPipelineStage
from pdpcli.settings import DEFAULT_COLT_SETTING
from pdpcli.data.data_reader import DataReader
from pdpcli.data.data_writer import DataWriter


class ConfigBuilder:
    @classmethod
    def build(cls, config: Dict[str, Any]) -> ConfigBuilder:
        colt_config = copy.deepcopy(DEFAULT_COLT_SETTING)
        colt_config.update(config.pop("colt", {}))

        builder = colt.build(config, cls=cls, **colt_config)

        return cast(ConfigBuilder, builder)

    def __init__(
        self,
        pipeline: PdPipelineStage,
        reader: Optional[DataReader] = None,
        writer: Optional[DataWriter] = None,
    ) -> None:
        self.pipeline = pipeline
        self.reader = reader
        self.writer = writer
