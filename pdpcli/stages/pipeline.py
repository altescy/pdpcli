from typing import Any, Dict, List, Union

import pdpipe

from pdpcli.stages.stage import Stage


@Stage.register("pipeline", exist_ok=True)
class Pipeline(pdpipe.PdPipeline):  # type: ignore
    def __init__(
        self,
        stages: Union[List[Stage], Dict[str, Stage]],
        **kwargs: Any,
    ) -> None:
        if isinstance(stages, dict):
            stages = list(stages.values())
        super().__init__(stages, **kwargs)
