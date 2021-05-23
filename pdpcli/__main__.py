#!/usr/bin/env python
import logging
import os
import sys

import colt

if os.environ.get("PDPCLI_DEBUG"):
    LEVEL = logging.DEBUG
else:
    LEVEL = logging.INFO

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir))))
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=LEVEL
)

from pdpcli.commands import main  # noqa: E402


def run() -> None:
    colt.import_modules(["pdpcli"])
    main(prog="pdp")


if __name__ == "__main__":
    run()
