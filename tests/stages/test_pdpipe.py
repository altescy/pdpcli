import colt
import pdpipe

from pdpcli.stages.stage import Stage


def test_pdpipe():
    stage = colt.build({"@type": "col_drop", "columns": "foo"}, cls=Stage)
    assert isinstance(stage, pdpipe.ColDrop)
