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

from sanic_ext.utils.typing import is_generic

from .check import Hint


def make_schema(agg, item):
    if type(item) in (bool, str, int, float):
        return agg

    if is_generic(item) and (args := get_args(item)):
        for arg in args:
            make_schema(agg, arg)
    elif item.__name__ not in agg and is_dataclass(item):
        sig = signature(item)
        hints = parse_hints(get_type_hints(item), item.__dataclass_fields__)

        agg[item.__name__] = {
            "sig": sig,
            "hints": hints,
        }

        for hint in hints.values():
            make_schema(agg, hint.hint)

    return agg


def parse_hints(hints, fields: Dict[str, Field]) -> Dict[str, Hint]:
    output: Dict[str, Hint] = {
        name: parse_hint(hint, fields.get(name))
        for name, hint in hints.items()
    }
    return output


def parse_hint(hint, field: Optional[Field] = None):
    origin = None
    literal = not isclass(hint)
    nullable = False
    typed = False
    model = False
    allowed: Tuple[Any, ...] = tuple()
    allow_missing = False

    if (
        field
        and field.default_factory  # type: ignore
        and field.default_factory is not MISSING  # type: ignore
    ):
        allow_missing = True

    if is_dataclass(hint):
        model = True
    elif is_generic(hint):
        typed = True
        literal = False
        origin = get_origin(hint)
        args = get_args(hint)
        nullable = origin == Union and type(None) in args

        if nullable:
            allowed = (args[0],)
        elif origin is dict:
            allowed = (args[1],)
        elif origin is list or origin is Literal or origin is Union:
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
