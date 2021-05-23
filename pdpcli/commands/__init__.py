import argparse
from typing import Optional

import colt

from pdpcli import __version__
from pdpcli.commands.subcommand import Subcommand
from pdpcli.plugins import import_plugins


def create_parser(prog: Optional[str] = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(usage="%(prog)s", prog=prog)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )

    subparsers = parser.add_subparsers()

    for subcommand in Subcommand.subcommands:
        subcommand.setup(subparsers)
        if subcommand.requires_plugins:
            subcommand.parser.add_argument(
                "--module",
                type=str,
                action="append",
                default=[],
                help="additional modules to include",
            )

    return parser


def main(prog: Optional[str] = None) -> None:
    import_plugins()

    parser = create_parser(prog)
    args = parser.parse_args()

    func = getattr(args, "func", None)
    if func is None:
        parser.parse_args(["--help"])

    if hasattr(args, "module"):
        colt.import_modules(args.module)

    func(args)
