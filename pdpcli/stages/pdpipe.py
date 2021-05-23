import inspect

import pdpipe

from pdpcli.stages.stage import Stage
from pdpcli.util import camel_to_snake


def load_pdpie_stages() -> None:
    # register PdPipeStages in pdpipe
    for pdpname, pdpcls in inspect.getmembers(pdpipe):
        if isinstance(pdpcls, type) and issubclass(pdpcls, pdpipe.PdPipelineStage):
            name = f"{camel_to_snake(pdpname)}"
            Stage.register(name)(pdpcls)
