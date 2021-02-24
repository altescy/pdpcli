from __future__ import annotations
from typing import cast, Any, Dict, Optional
import copy

import colt

from pdpcli.stages import Stage, PassThroughStage
from pdpcli.settings import DEFAULT_COLT_SETTING
from pdpcli.data.data_readers import DataReader
from pdpcli.data.data_writers import DataWriter


class ConfigBuilder:
    FIELDS = ["colt", "pipeline", "reader", "writer"]

    @classmethod
    def build(cls, config: Dict[str, Any]) -> ConfigBuilder:
        config = {
            key: value
            for key, value in config.items() if key in ConfigBuilder.FIELDS
        }

        colt_config = copy.deepcopy(DEFAULT_COLT_SETTING)
        colt_config.update(config.pop("colt", {}))

        builder = colt.build(config, cls=cls, **colt_config)

        return cast(ConfigBuilder, builder)

    def __init__(
        self,
        pipeline: Optional[Stage] = None,
        reader: Optional[DataReader] = None,
        writer: Optional[DataWriter] = None,
    ) -> None:
        self.pipeline = pipeline or PassThroughStage()
        self.reader = reader
        self.writer = writer
