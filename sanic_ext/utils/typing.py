import types
import typing

try:
    UnionType = types.UnionType  # type: ignore
except AttributeError:
    UnionType = type("UnionType", (), {})

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
