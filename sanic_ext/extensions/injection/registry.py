from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Set, Tuple, Type

from sanic.app import Sanic
from sanic.config import Config

from .constructor import Constructor


class InjectionRegistry:
    def __init__(self):
        self._registry: Dict[Type, Optional[Callable[..., Any]]] = {}

    def __getitem__(self, key):
        return self._registry[key]

    def __str__(self) -> str:
        return str(self._registry)

    def __contains__(self, other: Any):
        return other in self._registry

    def get(self, key, default=None):
        return self._registry.get(key, default)

    def register(
        self,
        _type: Type,
        constructor: Optional[Callable[..., Any]],
        request_arg: Optional[str] = None,
    ) -> None:
        constructor = constructor or _type
        constructor = Constructor(constructor, request_arg=request_arg)
        self._registry[_type] = constructor

    def finalize(
        self, app: Sanic, constant_registry: ConstantRegistry, allowed_types
    ):
        for constructor in self._registry.values():
            if isinstance(constructor, Constructor):
                constructor.prepare(
                    app, self, constant_registry, allowed_types
                )

    @property
    def length(self):
        return len(self._registry)


class SignatureRegistry:
    def __init__(self):
        self._registry: Dict[
            str,
            Tuple[
                Dict[str, Tuple[Type, Optional[Callable[..., Any]]]],
                Dict[str, Any],
            ],
        ] = {}

    def __getitem__(self, key):
        return self._registry[key]

    def __str__(self) -> str:
        return str(self._registry)

    def get(self, key, default=None):
        return self._registry.get(key, default)

    def register(
        self,
        route_name: str,
        dependencies: Dict[str, Tuple[Type, Optional[Callable[..., Any]]]],
        constants: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._registry[route_name] = (dependencies, constants or {})


class ConstantRegistry:
    def __init__(self, config: Config):
        self._config = config
        self._registry: Set[str] = set()

    def __str__(self) -> str:
        return str(self._registry)

    def __iter__(self):
        return iter(self._registry)

    def __getitem__(self, key):
        return self._registry[key]

    def __contains__(self, other: Any):
        return other in self._registry

    def register(self, key: str, value: Any, overwrite: bool):
        attribute = key.upper()
        if attribute in self._config and not overwrite:
            raise ValueError(
                f"A value for {attribute} has already been assigned"
            )
        key = key.lower()
        setattr(self._config, attribute, value)
        return self._registry.add(key)

    def get(self, key: str):
        key = key.lower()
        if key not in self._registry:
            raise ValueError
        attribute = key.upper()
        return getattr(self._config, attribute)

    @property
    def length(self):
        return len(self._registry)
