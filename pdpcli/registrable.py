from typing import Dict, List, Type, TypeVar, Union
from collections import defaultdict
from pathlib import Path

import colt

from pdpcli import util

T = TypeVar("T", bound="RegistrableWithFile")


class RegistrableWithFile(colt.Registrable):
    extensions: Dict[Type, Dict[str, str]] = defaultdict(dict)

    @classmethod
    def from_path(cls: Type[T], file_path: Union[str, Path], *args, **kwargs):
        registry = RegistrableWithFile.extensions[cls]
        ext = util.get_file_ext(file_path)
        if ext in registry:
            name = registry[ext]
            subclass = cls.by_name(name)
            return subclass(*args, **kwargs)
        return None

    @classmethod
    def register(cls, name: str, extensions: List[str] = None, **kwargs):
        # pylint: disable=arguments-differ
        super_register_fn = super().register(name, **kwargs)

        def decorator(subclass: Type[T]):
            super_register_fn(subclass)
            if extensions is not None:
                for ext in extensions:
                    RegistrableWithFile.extensions[cls][ext] = name

            return subclass

        return decorator
