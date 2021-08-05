from ..base import Extension
from .injector import add_injection
from .registry import InjectionRegistry


class InjectionExtension(Extension):
    name = "injection"

    def startup(self, bootstrap) -> None:
        registry = InjectionRegistry()
        add_injection(self.app, registry)
        bootstrap._injection_registry = registry
