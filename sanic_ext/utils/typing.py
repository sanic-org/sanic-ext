import types
import typing


def is_generic(item):
    return (
        isinstance(item, typing._GenericAlias)
        or isinstance(item, types.UnionType)
        or hasattr(item, "__origin__")
    )
