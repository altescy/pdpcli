import inspect

import pdpipe

from pdpcli.util import camel_to_snake
from pdpcli.stages.stage import Stage


def load_pdpie_stages():
    # register PdPipeStages in pdpipe
    for pdpname, pdpcls in inspect.getmembers(pdpipe):
        if isinstance(pdpcls, type) and issubclass(pdpcls,
                                                   pdpipe.PdPipelineStage):
            name = f"{camel_to_snake(pdpname)}"
            Stage.register(name)(pdpcls)
