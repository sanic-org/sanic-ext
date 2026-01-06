from __future__ import annotations

from inspect import isclass, iscoroutine
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from sanic import Request

from .constructor import Constructor


if TYPE_CHECKING:
    from sanic import Sanic

    from .registry import InjectionRegistry


def create_command_wrapper(func: Callable, app: Sanic) -> Callable:
    original = _unwrap(func)

    async def wrapped(**kwargs):
        ext = getattr(app, "_ext", None)
        registry = getattr(ext, "_injection_registry", None) if ext else None
        if not registry:
            return await _maybe_await(func(**kwargs))

        hints = _get_hints(original)
        kwargs = await _inject_dependencies(kwargs, hints, registry)
        kwargs = _inject_constants(kwargs, hints, ext, app)
        return await _maybe_await(func(**kwargs))

    return wrapped


def _unwrap(func: Callable) -> Callable:
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


def _get_hints(func: Callable) -> dict[str, Any]:
    try:
        target = func.__init__ if isclass(func) else func
        hints = get_type_hints(target)
    except (NameError, TypeError, AttributeError):
        return {}
    hints.pop("return", None)
    hints.pop("self", None)
    return hints


async def _maybe_await(result: Any) -> Any:
    if iscoroutine(result):
        return await result
    return result


async def _inject_dependencies(
    kwargs: dict, hints: dict, registry: InjectionRegistry
) -> dict:
    for param, annotation in hints.items():
        if param in kwargs and kwargs[param] is not None:
            continue
        if annotation in registry:
            kwargs[param] = await _resolve(annotation, registry)
    return kwargs


def _inject_constants(kwargs: dict, hints: dict, ext: Any, app: Sanic) -> dict:
    constant_registry = getattr(ext, "_constant_registry", None)
    if not constant_registry:
        return kwargs
    for param in hints:
        if kwargs.get(param) is None and param.lower() in constant_registry:
            kwargs[param] = getattr(app.config, param.upper(), None)
    return kwargs


async def _resolve(annotation: type, registry: InjectionRegistry) -> Any:
    constructor = registry.get(annotation)
    if constructor is None:
        return annotation()
    if not isinstance(constructor, Constructor):
        return await _maybe_await(constructor())

    hints = _get_hints(constructor.func)
    nested_kwargs = await _resolve_nested(annotation, hints, registry)
    return await _maybe_await(constructor.func(**nested_kwargs))


async def _resolve_nested(
    annotation: type, hints: dict, registry: InjectionRegistry
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, param_type in hints.items():
        if _is_optional_request(param_type):
            continue
        if _is_required_request(param_type):
            raise RuntimeError(
                f"Cannot inject {getattr(annotation, '__name__', str(annotation))} into command handler: "
                f"the constructor requires a Request object."
            )
        if param_type in registry:
            result[name] = await _resolve(param_type, registry)
    return result


def _is_optional_request(param_type: type) -> bool:
    if get_origin(param_type) is not Union:
        return False
    args = get_args(param_type)
    if len(args) != 2 or type(None) not in args:
        return False
    other = args[0] if args[1] is type(None) else args[1]
    return isclass(other) and issubclass(other, Request)


def _is_required_request(param_type: type) -> bool:
    return isclass(param_type) and issubclass(param_type, Request)
