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


def is_optional(item):
    if is_generic(item):
        args = typing.get_args(item)
        return len(args) == 2 and type(None) in args
    return False
