from __future__ import annotations

from inspect import signature
from typing import TYPE_CHECKING, get_type_hints

from sanic.models.futures import FutureCommand

from ..base import Extension
from .command_wrapper import _unwrap, create_command_wrapper
from .injector import add_injection
from .registry import ConstantRegistry, InjectionRegistry


if TYPE_CHECKING:
    from sanic import Sanic


class InjectionExtension(Extension):
    name = "injection"

    def startup(self, bootstrap) -> None:
        self.constant_registry = ConstantRegistry(self.app.config)
        self.registry = InjectionRegistry()
        add_injection(self.app, self.registry, self.constant_registry)
        self.app._future_commands = _InjectionCommandSet(
            self.app, self.registry, self.app._future_commands
        )
        bootstrap._injection_registry = self.registry
        bootstrap._constant_registry = self.constant_registry
        if self.config.INJECTION_LOAD_CUSTOM_CONSTANTS:
            self.app.ext.load_constants()

    def label(self):
        return (
            f"{self.registry.length} dependencies; "
            f"{self.constant_registry.length} constants"
        )


class _InjectionCommandSet(set):
    """A set that wraps commands with dependency injection when added."""

    def __init__(self, app: Sanic, registry: InjectionRegistry, initial=()):
        super().__init__()
        self._app = app
        self._registry = registry
        for cmd in initial:
            self.add(cmd)

    def add(self, cmd: FutureCommand) -> None:
        original = _unwrap(cmd.func)
        wrapped = create_command_wrapper(original, self._app)

        try:
            hints = get_type_hints(original)
        except Exception:
            hints = getattr(original, "__annotations__", {})

        orig_sig = signature(original)
        new_params = [
            p
            for p in orig_sig.parameters.values()
            if hints.get(p.name) not in self._registry
        ]
        wrapped.__signature__ = orig_sig.replace(parameters=new_params)

        super().add(FutureCommand(cmd.name, wrapped))
