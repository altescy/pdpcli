from __future__ import annotations

import copy
from typing import Any, Dict, Optional, cast

import colt

from pdpcli.data.data_readers import DataReader
from pdpcli.data.data_writers import DataWriter
from pdpcli.settings import DEFAULT_COLT_SETTING
from pdpcli.stages import PassThroughStage, Stage


class ConfigBuilder:
    FIELDS = ["colt", "pipeline", "reader", "writer"]

    @classmethod
    def build(cls, config: Dict[str, Any]) -> ConfigBuilder:
        config = {
            key: value for key, value in config.items() if key in ConfigBuilder.FIELDS
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
