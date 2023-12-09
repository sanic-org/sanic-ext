import types
import typing

from inspect import isclass


try:
    UnionType = types.UnionType  # type: ignore
except AttributeError:
    UnionType = type("UnionType", (), {})  # type: ignore

try:
    from pydantic import BaseModel

    PYDANTIC = True
except ImportError:
    PYDANTIC = False

try:
    import attrs  # noqa

    ATTRS = True
except ImportError:
    ATTRS = False

try:
    from msgspec import Struct

    MSGSPEC = True
except ImportError:
    MSGSPEC = False


def is_generic(item):
    return (
        isinstance(item, typing._GenericAlias)
        or isinstance(item, UnionType)
        or hasattr(item, "__origin__")
    )


def is_optional(item):
    if is_generic(item):
        args = typing.get_args(item)
        return len(args) == 2 and type(None) in args
    return False


def is_pydantic(model):
    return PYDANTIC and (
        issubclass(model, BaseModel) or hasattr(model, "__pydantic_model__")
    )


def is_attrs(model):
    return ATTRS and (hasattr(model, "__attrs_attrs__"))


def is_msgspec(model):
    return MSGSPEC and issubclass(model, Struct)


def flat_values(
    item: typing.Union[
        typing.Dict[str, typing.Any], typing.Iterable[typing.Any]
    ],
) -> typing.Set[typing.Any]:
    values = set()
    if isinstance(item, dict):
        item = item.values()
    for value in item:
        if isinstance(value, dict) or isinstance(value, list):
            values.update(flat_values(value))
        else:
            values.add(value)
    return values


def contains_annotations(d: typing.Dict[str, typing.Any]) -> bool:
    values = flat_values(d)
    return any(isclass(q) or is_generic(q) for q in values)
