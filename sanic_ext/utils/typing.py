import types
import typing

try:
    UnionType = types.UnionType  # type: ignore
except AttributeError:
    UnionType = type("UnionType", (), {})


def is_generic(item):
    return (
        isinstance(item, typing._GenericAlias)
        or isinstance(item, UnionType)
        or hasattr(item, "__origin__")
    )
