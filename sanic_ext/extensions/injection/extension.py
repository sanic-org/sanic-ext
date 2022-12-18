from ..base import Extension
from .injector import add_injection
from .registry import ConstantRegistry, InjectionRegistry


class InjectionExtension(Extension):
    name = "injection"

    def startup(self, bootstrap) -> None:
        self.constant_registry = ConstantRegistry(self.app.config)
        self.registry = InjectionRegistry()
        add_injection(self.app, self.registry, self.constant_registry)
        bootstrap._injection_registry = self.registry
        bootstrap._constant_registry = self.constant_registry
        self.app.ext.load_constants()

    def label(self):
        return f"{self.registry.length} added"
