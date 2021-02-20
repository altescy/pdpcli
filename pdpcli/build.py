import colt
import pdpipe

from pdpcli.stages import PdpipelineStage


def build_pdpipe(config, **kwrags) -> pdpipe.PdPipelineStage:
    obj = colt.build(config, cls=PdpipelineStage, **kwrags)
    return obj
