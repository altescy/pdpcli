from typing import List
import inspect

import colt
import pandas
import pdpipe

from pdpcli.util import camel_to_snake


class PdpipelineStage(pdpipe.PdPipelineStage, colt.Registrable):
    # pylint: disable=abstract-method
    pass


# register PdPipeStages in pdpipe
for pdpname, pdpcls in inspect.getmembers(pdpipe):
    if isinstance(pdpcls, type) and issubclass(pdpcls, pdpipe.PdPipelineStage):
        name = f"{camel_to_snake(pdpname)}"
        PdpipelineStage.register(name)(pdpcls)


@PdpipelineStage.register("pipeline", exist_ok=True)
class PdPipelineWrapper(pdpipe.PdPipeline):  # pylint: disable=too-many-ancestors
    def __init__(self, stages: List[PdpipelineStage], **kwargs) -> None:
        super().__init__(stages, **kwargs)
