from typing import Dict, List, Union

import pdpipe

from pdpcli.stages.stage import Stage


@Stage.register("pipeline", exist_ok=True)
class Pipeline(pdpipe.PdPipeline):  # pylint: disable=too-many-ancestors
    def __init__(
        self,
        stages: Union[List[Stage], Dict[str, Stage]],
        **kwargs,
    ) -> None:
        if isinstance(stages, dict):
            stages = list(stages.values())
        super().__init__(stages, **kwargs)
