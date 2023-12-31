from __future__ import annotations

from functools import partial
from inspect import getmembers, isclass, isfunction
from typing import Any, Callable, Dict, Optional, Tuple, Type, get_type_hints

from sanic import Sanic
from sanic.constants import HTTP_METHODS

from sanic_ext.config import PRIORITY
from sanic_ext.extensions.injection.constructor import gather_args

from .registry import ConstantRegistry, InjectionRegistry, SignatureRegistry


def add_injection(
    app: Sanic,
    injection_registry: InjectionRegistry,
    constant_registry: ConstantRegistry,
) -> None:
    signature_registry = _setup_signature_registry(
        app, injection_registry, constant_registry
    )

    @app.listener("before_server_start", priority=PRIORITY)
    async def finalize_injections(app: Sanic, _):
        router_converters = set(
            allowed[0] for allowed in app.router.regex_types.values()
        )
        router_types = set()
        for converter in router_converters:
            if isclass(converter):
                router_types.add(converter)
            elif isfunction(converter):
                hints = get_type_hints(converter)
                if return_type := hints.get("return"):
                    router_types.add(return_type)
        injection_registry.finalize(app, constant_registry, router_types)

    injection_signal = app.ext.config.INJECTION_SIGNAL
    injection_priority = app.ext.config.INJECTION_PRIORITY

    @app.signal(injection_signal, priority=injection_priority)
    async def inject_kwargs(request, **_):
        nonlocal signature_registry

        for name in (
            request.route.name,
            f"{request.route.name}_{request.method.lower()}",
        ):
            dependencies, constants = signature_registry.get(
                name, (None, None)
            )
            if dependencies or constants:
                break

        if dependencies:
            injected_args = await gather_args(
                dependencies, request, **request.match_info
            )
            request.match_info.update(injected_args)
        if constants:
            request.match_info.update(constants)


def _http_method_predicate(member):
    return isfunction(member) and member.__name__ in HTTP_METHODS


def _setup_signature_registry(
    app: Sanic,
    injection_registry: InjectionRegistry,
    constant_registry: ConstantRegistry,
) -> SignatureRegistry:
    registry = SignatureRegistry()

    @app.listener("before_server_start", priority=PRIORITY - 1)
    async def setup_signatures(app, _):
        nonlocal registry

        for route in app.router.routes:
            if ".openapi." in route.name:
                continue
            handlers = [(route.name, route.handler)]
            viewclass = getattr(route.handler, "view_class", None)
            if viewclass:
                handlers = [
                    (f"{route.name}_{name}", member)
                    for name, member in getmembers(
                        viewclass, _http_method_predicate
                    )
                ]
            for name, handler in handlers:
                if route_handler := getattr(
                    handler, "__route_handler__", None
                ):
                    handler = route_handler
                if isinstance(handler, partial):
                    if handler.func == app._websocket_handler:
                        handler = handler.args[0]
                    else:
                        handler = handler.func
                try:
                    hints = get_type_hints(handler)
                except TypeError:
                    continue

                dependencies: Dict[
                    str, Tuple[Type, Optional[Callable[..., Any]]]
                ] = {}
                constants: Dict[str, Any] = {}
                for param, annotation in hints.items():
                    if annotation in injection_registry:
                        dependencies[param] = (
                            annotation,
                            injection_registry[annotation],
                        )
                    if param in constant_registry:
                        constants[param] = app.config[param.upper()]

                registry.register(name, dependencies, constants)

    return registry
