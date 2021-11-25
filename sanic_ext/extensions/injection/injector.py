from inspect import Signature, getmembers, isawaitable, isfunction, signature
from typing import Any, Callable, Dict, Optional, Tuple, Type

from sanic import Sanic
from sanic.constants import HTTP_METHODS

from .registry import InjectionRegistry, SignatureRegistry


def add_injection(app: Sanic, injection_registry: InjectionRegistry) -> None:
    signature_registry = _setup_signature_registry(app, injection_registry)

    @app.signal("http.routing.after")
    async def inject_kwargs(request, route, kwargs, **_):
        nonlocal signature_registry

        for name in (route.name, f"{route.name}_{request.method.lower()}"):
            injections = signature_registry[name]
            if injections:
                break

        if injections:
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
                sig = signature(handler)
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
                registry.register(name, injections)

    return registry
