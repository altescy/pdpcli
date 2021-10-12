from typing import Any, Dict

import pdpipe

from pdpcli.stages.stage import Stage


@Stage.register("pipeline", exist_ok=True)
class Pipeline(pdpipe.PdPipeline):  # type: ignore
    def __init__(
        self,
        stages: Dict[str, Stage],
        **kwargs: Any,
    ) -> None:
        super().__init__(list(stages.values()), **kwargs)
