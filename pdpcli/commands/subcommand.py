from __future__ import annotations

import argparse
from typing import Callable, List, Optional, Type


class Subcommand:
    requires_plugins: bool = True
    subcommands: List["Subcommand"] = []

    @classmethod
    def register(
        cls, name: str, description: str, help: str
    ) -> Callable[[Type[Subcommand]], Type[Subcommand]]:
        def decorator(T: Type[Subcommand]) -> Type[Subcommand]:
            subcommand = T(name, description, help)
            Subcommand.subcommands.append(subcommand)
            return T

        return decorator

    def __init__(self, name: str, description: str, help_: str) -> None:
        self._name = name
        self._description = description
        self._help = help_

        self._parser: Optional[argparse.ArgumentParser] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def parser(self) -> argparse.ArgumentParser:
        if self._parser is None:
            raise RuntimeError("parser is not set")
        return self._parser

    def setup(
        self, subparsers: argparse._SubParsersAction
    ) -> None:  # pylint: disable=protected-access
        self._parser = subparsers.add_parser(
            self._name,
            description=self._description,
            help=self._help,
        )
        self.set_arguments()
        self.parser.set_defaults(func=self.run)

    def set_arguments(self) -> None:
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> None:
        raise NotImplementedError
