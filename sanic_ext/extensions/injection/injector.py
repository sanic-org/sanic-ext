from __future__ import annotations

from functools import partial
from inspect import getmembers, isclass, isfunction
from typing import Any, Callable, Dict, Optional, Tuple, Type, get_type_hints

from sanic import Request, Sanic
from sanic.constants import HTTP_METHODS
from sanic.signals import Event

from sanic_ext.extensions.injection.constructor import gather_args

from .registry import InjectionRegistry, SignatureRegistry

BEFORE_HANDLER_EXISTS = False
try:  # Only available in Sanic >= XX.X
    Event.HTTP_HANDLER_BEFORE
except AttributeError:
    ...
else:
    BEFORE_HANDLER_EXISTS = True


def add_injection(app: Sanic, injection_registry: InjectionRegistry) -> None:
    signature_registry = _setup_signature_registry(app, injection_registry)

    async def inject_kwargs(request: Request, **_):
        injections = None

        route = request.route
        # ↓ With the allowed signals this is true
        assert route is not None

        for name in (
            route.name,
            f"{route.name}_{request.method.lower()}",
        ):
            injections = signature_registry.get(name)
            if injections:
                break

        if injections:
            injected_args = await gather_args(
                injections, request, **request.match_info
            )
            request.match_info.update(injected_args)

    @app.signal(Event.HTTP_ROUTING_AFTER)
    async def after_routing_inject(request: Request, **_):
        if Event.HTTP_ROUTING_AFTER not in injection_registry.signals:
            return
        return await inject_kwargs(request)

    if BEFORE_HANDLER_EXISTS:

        @app.signal(Event.HTTP_HANDLER_BEFORE)
        async def before_handler_inject(request: Request, **_):
            if Event.HTTP_HANDLER_BEFORE not in injection_registry.signals:
                return
            return await inject_kwargs(request)

    @app.after_server_start
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
        injection_registry.finalize(router_types)


def _http_method_predicate(member):
    return isfunction(member) and member.__name__ in HTTP_METHODS


def _setup_signature_registry(
    app: Sanic,
    injection_registry: InjectionRegistry,
) -> SignatureRegistry:
    registry = SignatureRegistry()

    @app.after_server_start
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
                if hasattr(handler, "__auto_handler__"):
                    continue
                if isinstance(handler, partial):
                    if handler.func == app._websocket_handler:
                        handler = handler.args[0]
                    else:
                        handler = handler.func
                try:
                    hints = get_type_hints(handler)
                except TypeError:
                    continue

                injections: Dict[
                    str, Tuple[Type, Optional[Callable[..., Any]]]
                ] = {
                    param: (
                        annotation,
                        injection_registry[annotation],
                    )
                    for param, annotation in hints.items()
                    if annotation in injection_registry
                }
                registry.register(name, injections)

    return registry
