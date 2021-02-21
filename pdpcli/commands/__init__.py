import argparse

import colt

from pdpcli import __version__
from pdpcli.commands.subcommand import Subcommand


def main(prog: str = None):
    parser = argparse.ArgumentParser(usage='%(prog)s', prog=prog)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    parser.add_argument(
        "--module",
        type=str,
        action="append",
        default=[],
        help="additional modules to include",
    )

    subparsers = parser.add_subparsers()

    for subcommand in Subcommand.subcommands:
        subcommand.setup(subparsers)

    args = parser.parse_args()
    func = getattr(args, "func", None)

    colt.import_modules(args.module)

    if func is not None:
        func(args)
    else:
        parser.parse_args(["--help"])
