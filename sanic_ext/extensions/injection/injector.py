from inspect import Signature, isawaitable, signature
from typing import Any, Callable, Dict, Optional, Tuple, Type

from sanic import Sanic

from .registry import InjectionRegistry, SignatureRegistry


def add_injection(app: Sanic, injection_registry: InjectionRegistry) -> None:
    signature_registry = _setup_signature_registry(app, injection_registry)

    @app.signal("http.routing.after")
    async def inject_kwargs(request, route, kwargs, **_):
        nonlocal signature_registry

        injections = signature_registry[route.name]

        injected_args = {
            name: await _do_cast(_type, constructor, request, **kwargs)
            for name, (_type, constructor) in injections.items()
        }
        request.match_info.update(injected_args)


async def _do_cast(_type, constructor, request, **kwargs):
    cast = constructor if constructor else _type
    args = [request] if constructor else []
    retval = cast(*args, **kwargs)
    if isawaitable(retval):
        retval = await retval
    return retval


def _setup_signature_registry(
    app: Sanic,
    injection_registry: InjectionRegistry,
) -> SignatureRegistry:
    registry = SignatureRegistry()

    @app.after_server_start
    async def setup_signatures(app, _):
        nonlocal registry

        for route in app.router.routes:
            sig = signature(route.handler)
            injections: Dict[
                str, Tuple[Type, Optional[Callable[..., Any]]]
            ] = {
                param.name: (
                    param.annotation,
                    injection_registry[param.annotation],
                )
                for param in sig.parameters.values()
                if param.annotation != Signature.empty
                and param.annotation in injection_registry._registry
            }
            registry.register(route.name, injections)

    return registry
