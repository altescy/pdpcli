from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

import colt

from pdpcli import util

T = TypeVar("T", bound="RegistrableWithFile")


class RegistrableWithFile(colt.Registrable):  # type: ignore
    extensions: Dict[Type, Dict[str, str]] = defaultdict(dict)  # type: ignore

    @classmethod
    def from_path(
        cls: Type[T],
        file_path: Union[str, Path],
        *args: Any,
        **kwargs: Any,
    ) -> Optional[RegistrableWithFile]:
        registry = RegistrableWithFile.extensions[cls]
        ext = util.get_file_ext(file_path)
        if ext in registry:
            name = registry[ext]
            subclass = cls.by_name(name)
            return cast(RegistrableWithFile, subclass(*args, **kwargs))
        return None

    @classmethod
    def register(
        cls,
        name: str,
        extensions: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Callable[[Type[T]], Type[T]]:
        super_register_fn = super().register(name, **kwargs)

        def decorator(subclass: Type[T]) -> Type[T]:
            super_register_fn(subclass)
            if extensions is not None:
                for ext in extensions:
                    RegistrableWithFile.extensions[cls][ext] = name

            return subclass

        return decorator
