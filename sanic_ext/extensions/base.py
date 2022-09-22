from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Union

from sanic.app import Sanic
from sanic.exceptions import SanicException

from sanic_ext.config import Config
from sanic_ext.exceptions import InitError


class NoDuplicateDict(dict):  # type: ignore
    def __setitem__(self, key: Any, value: Any) -> None:
        if key in self:
            raise KeyError(f"Duplicate key: {key}")
        return super().__setitem__(key, value)


class Extension(ABC):
    _name_registry: Dict[str, Type[Extension]] = NoDuplicateDict()
    _started: bool
    name: str
    app: Sanic
    config: Config

    def __init_subclass__(cls):
        if not getattr(cls, "name", None) or not cls.name.isalpha():
            raise InitError(
                "Extensions must be named, and may only contain "
                "alphabetic characters"
            )

        if cls.name in cls._name_registry:
            raise InitError(f'Extension "{cls.name}" already exists')

        cls._name_registry[cls.name] = cls

    def _startup(self, bootstrap):
        if self._started:
            raise SanicException(
                "Extension already started. Cannot start "
                f"Extension:{self.name} multiple times."
            )
        self.startup(bootstrap)
        self._started = True

    @abstractmethod
    def startup(self, bootstrap) -> None:
        ...

    def label(self):
        return ""

    def render_label(self):
        if not self.included:
            return "~~disabled~~"
        label = self.label()
        if not label:
            return ""
        return f"[{label}]"

    def included(self):
        return True

    @classmethod
    def create(
        cls,
        extension: Union[Type[Extension], Extension],
        app: Sanic,
        config: Config,
    ) -> Extension:
        instance = (
            extension if isinstance(extension, Extension) else extension()
        )
        instance.app = app
        instance.config = config
        instance._started = False
        return instance

    @classmethod
    def reset(cls) -> None:
        cls._name_registry.clear()
