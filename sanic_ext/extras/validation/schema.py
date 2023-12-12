import types

from dataclasses import MISSING, Field, is_dataclass
from inspect import isclass, signature
from typing import (
    Any,
    Dict,
    Literal,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from sanic_ext.utils.typing import is_attrs, is_generic, is_msgspec

from .check import Hint


try:
    UnionType = types.UnionType  # type: ignore
except AttributeError:
    UnionType = type("UnionType", (), {})

try:
    from attr import NOTHING, Attribute
except ModuleNotFoundError:
    NOTHING = object()  # type: ignore
    Attribute = type("Attribute", (), {})  # type: ignore

try:
    from msgspec.inspect import type_info as msgspec_type_info
except ModuleNotFoundError:

    def msgspec_type_info(val):
        pass


def make_schema(agg, item):
    if type(item) in (bool, str, int, float):
        return agg

    if is_generic(item) and (args := get_args(item)):
        for arg in args:
            make_schema(agg, arg)
    elif item.__name__ not in agg and (
        is_dataclass(item) or is_attrs(item) or is_msgspec(item)
    ):
        if is_dataclass(item):
            fields = item.__dataclass_fields__
        elif is_msgspec(item):
            fields = {f.name: f.type for f in msgspec_type_info(item).fields}
        else:
            fields = {attr.name: attr for attr in item.__attrs_attrs__}

        sig = signature(item)
        hints = parse_hints(get_type_hints(item), fields)

        agg[item.__name__] = {
            "sig": sig,
            "hints": hints,
        }

        for hint in hints.values():
            make_schema(agg, hint.hint)

    return agg


def parse_hints(
    hints, fields: Dict[str, Union[Field, Attribute]]
) -> Dict[str, Hint]:
    output: Dict[str, Hint] = {
        name: parse_hint(hint, fields.get(name))
        for name, hint in hints.items()
    }
    return output


def parse_hint(hint, field: Optional[Union[Field, Attribute]] = None):
    origin = None
    literal = not isclass(hint)
    nullable = False
    typed = False
    model = False
    allowed: Tuple[Any, ...] = tuple()
    allow_missing = False

    if field and (
        (
            isinstance(field, Field) and field.default_factory is not MISSING  # type: ignore
        )
        or (isinstance(field, Attribute) and field.default is not NOTHING)
    ):
        allow_missing = True

    if is_dataclass(hint) or is_attrs(hint):
        model = True
    elif is_generic(hint):
        typed = True
        literal = False
        origin = get_origin(hint)
        args = get_args(hint)
        nullable = origin in (Union, UnionType) and type(None) in args

        if nullable:
            allowed = tuple(
                [
                    arg
                    for arg in args
                    if is_generic(arg) or not isinstance(None, arg)
                ]
            )
        elif origin is dict:
            allowed = (args[1],)
        elif (
            origin is list
            or origin is Literal
            or origin is Union
            or origin is UnionType
        ):
            allowed = args

    return Hint(
        hint,
        model,
        literal,
        typed,
        nullable,
        origin,
        tuple([parse_hint(item, None) for item in allowed]),
        allow_missing,
    )
