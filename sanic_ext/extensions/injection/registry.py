from typing import Any, Callable, Dict, Optional, Tuple, Type


class InjectionRegistry:
    def __init__(self):
        self._registry: Dict[Type, Optional[Callable[..., Any]]] = {}

    def __getitem__(self, key):
        return self._registry[key]

    def __str__(self) -> str:
        return str(self._registry)

    def register(
        self, _type: Type, constructor: Optional[Callable[..., Any]]
    ) -> None:
        self._registry[_type] = constructor


class SignatureRegistry:
    def __init__(self):
        self._registry: Dict[
            str, Dict[str, Tuple[Type, Optional[Callable[..., Any]]]]
        ] = {}

    def __getitem__(self, key):
        return self._registry[key]

    def __str__(self) -> str:
        return str(self._registry)

    def register(
        self,
        route_name: str,
        injections: Dict[str, Tuple[Type, Optional[Callable[..., Any]]]],
    ) -> None:
        self._registry[route_name] = injections
