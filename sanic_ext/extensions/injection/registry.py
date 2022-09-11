from typing import Any, Callable, Dict, Optional, Tuple, Type

from collections import defaultdict

from sanic.exceptions import SanicException
from sanic.signals import Event

from .constructor import Constructor


class InjectionRegistry:
    def __init__(self):
        self._registry: Dict[
            Event, Dict[Type, Optional[Callable[..., Any]]]
        ] = defaultdict(dict)

    def __getitem__(self, key):
        item = self.get(key)
        if item is None:
            raise KeyError(key)
        return item

    def __str__(self) -> str:
        return str(self._registry)

    def __contains__(self, other: Any):
        return self.get(other) is not None

    def get(self, key, default=None):
        for signal_registry in self._registry.values():
            if key in signal_registry:
                return signal_registry[key]
        return default

    @property
    def signals(self):
        return self._registry.keys()

    def register(
        self,
        _type: Type,
        constructor: Optional[Callable[..., Any]],
        signal: Event,
    ) -> None:
        if constructor:
            constructor = Constructor(constructor)

        if self.get(_type) is not None:
            raise SanicException(
                "There is already an injection registered for "
                f"{_type.__name__}"
            )

        self._registry[signal][_type] = constructor

    def finalize(self, allowed_types):
        for signal_registry in self._registry.values():
            for constructor in signal_registry.values():
                if isinstance(constructor, Constructor):
                    constructor.prepare(self, allowed_types)

    @property
    def length(self):
        return len(self._registry)


class SignatureRegistry:
    def __init__(self):
        self._registry: Dict[
            str, Dict[str, Tuple[Type, Optional[Callable[..., Any]]]]
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
        injections: Dict[str, Tuple[Type, Optional[Callable[..., Any]]]],
    ) -> None:
        self._registry[route_name] = injections
