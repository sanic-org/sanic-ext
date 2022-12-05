from dataclasses import dataclass, field
from typing import List

from sanic.constants import HTTPMethod
from sanic_routing.route import Route

from .decorators import Definition


@dataclass
class Path:
    route: Route
    method: HTTPMethod
    definitions: List[Definition] = field(default_factory=list)


@dataclass
class Paths:
    _items: List[Path] = field(default_factory=list)

    def register(self, item: Path) -> None:
        self._items.append(item)
