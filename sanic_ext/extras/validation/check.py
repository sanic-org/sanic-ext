from __future__ import annotations

from dataclasses import _HAS_DEFAULT_FACTORY  # type: ignore
from typing import (
    Any,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    get_args,
    get_origin,
)

from sanic_ext.utils.typing import (
    UnionType,
    is_generic,
    is_msgspec,
    is_optional,
)


MISSING: Tuple[Any, ...] = (_HAS_DEFAULT_FACTORY,)

try:
    import attrs  # noqa

    NOTHING = attrs.NOTHING
    ATTRS = True
    MISSING = (
        _HAS_DEFAULT_FACTORY,
        NOTHING,
    )
except ImportError:
    ATTRS = False


try:
    import msgspec

    MSGSPEC = True
except ImportError:
    MSGSPEC = False


class Hint(NamedTuple):
    hint: Any
    model: bool
    literal: bool
    typed: bool
    nullable: bool
    origin: Optional[Any]
    allowed: Tuple[Hint, ...]  # type: ignore
    allow_missing: bool

    def validate(
        self, value, schema, allow_multiple=False, allow_coerce=False
    ):
        if not self.typed:
            if self.model:
                return check_data(
                    self.hint,
                    value,
                    schema,
                    allow_multiple=allow_multiple,
                    allow_coerce=allow_coerce,
                )

            if (
                allow_multiple
                and isinstance(value, list)
                and self.coerce_type is not list
                and len(value) == 1
            ):
                value = value[0]
            try:
                _check_types(value, self.literal, self.hint)
            except ValueError as e:
                if allow_coerce:
                    value = self.coerce(value)
                    _check_types(value, self.literal, self.hint)
                else:
                    raise e
        else:
            value = _check_nullability(
                value,
                self.nullable,
                self.allowed,
                schema,
                allow_multiple,
                allow_coerce,
            )

            if not self.nullable:
                if self.origin in (Union, Literal, UnionType):
                    value = _check_inclusion(
                        value,
                        self.allowed,
                        schema,
                        allow_multiple,
                        allow_coerce,
                    )
                elif self.origin is list:
                    value = _check_list(
                        value,
                        self.allowed,
                        self.hint,
                        schema,
                        allow_multiple,
                        allow_coerce,
                    )
                elif self.origin is dict:
                    value = _check_dict(
                        value,
                        self.allowed,
                        self.hint,
                        schema,
                        allow_multiple,
                        allow_coerce,
                    )

            if allow_coerce:
                value = self.coerce(value)

        return value

    def coerce(self, value):
        if is_generic(self.coerce_type):
            args = get_args(self.coerce_type)
            if get_origin(self.coerce_type) == Literal or (
                all(get_origin(arg) == Literal for arg in args)
            ):
                return value
            if type(None) in args and value is None:
                return None
            coerce_types = [arg for arg in args if not isinstance(None, arg)]
        else:
            coerce_types = [self.coerce_type]
        for coerce_type in coerce_types:
            try:
                if isinstance(value, list):
                    value = [coerce_type(item) for item in value]
                else:
                    value = coerce_type(value)
            except (ValueError, TypeError):
                ...
            else:
                return value
        return value

    @property
    def coerce_type(self):
        coerce_type = self.hint
        if is_optional(coerce_type):
            coerce_type = get_args(self.hint)[0]
        return coerce_type


def check_data(model, data, schema, allow_multiple=False, allow_coerce=False):
    if not isinstance(data, dict):
        raise TypeError(f"Value '{data}' is not a dict")
    sig = schema[model.__name__]["sig"]
    hints = schema[model.__name__]["hints"]
    bound = sig.bind(**data)
    bound.apply_defaults()
    params = dict(zip(sig.parameters, bound.args))
    params.update(bound.kwargs)

    hydration_values = {}
    try:
        for key, value in params.items():
            hint = hints.get(key, Any)
            try:
                hydration_values[key] = hint.validate(
                    value,
                    schema,
                    allow_multiple=allow_multiple,
                    allow_coerce=allow_coerce,
                )
            except ValueError:
                if not hint.allow_missing or value not in MISSING:
                    raise
    except ValueError as e:
        raise TypeError(e)

    if MSGSPEC and is_msgspec(model):
        try:
            return msgspec.from_builtins(
                hydration_values, model, str_values=True, str_keys=True
            )
        except msgspec.ValidationError as e:
            raise TypeError(e)
    else:
        return model(**hydration_values)


def _check_types(value, literal, expected):
    if literal:
        if expected is Any:
            return
        elif value != expected:
            raise ValueError(f"Value '{value}' must be {expected}")
    else:
        if MSGSPEC and is_msgspec(expected) and isinstance(value, Mapping):
            try:
                expected(**value)
            except (TypeError, msgspec.ValidationError):
                raise ValueError(f"Value '{value}' is not of type {expected}")
        elif not isinstance(value, expected):
            raise ValueError(f"Value '{value}' is not of type {expected}")


def _check_nullability(
    value, nullable, allowed, schema, allow_multiple, allow_coerce
):
    if not nullable and value is None:
        raise ValueError("Value cannot be None")
    if nullable and value is not None:
        exc = None
        for hint in allowed:
            try:
                value = hint.validate(
                    value, schema, allow_multiple, allow_coerce
                )
            except ValueError as e:
                exc = e
            else:
                break
        else:
            if exc:
                if len(allowed) == 1:
                    raise exc
                else:
                    options = ", ".join(
                        [str(option.hint) for option in allowed]
                    )
                    raise ValueError(
                        f"Value '{value}' must be one of {options}, or None"
                    )
    return value


def _check_inclusion(value, allowed, schema, allow_multiple, allow_coerce):
    for option in allowed:
        try:
            return option.validate(value, schema, allow_multiple, allow_coerce)
        except (ValueError, TypeError):
            ...

    options = ", ".join([str(option.hint) for option in allowed])
    raise ValueError(f"Value '{value}' must be one of {options}")


def _check_list(value, allowed, hint, schema, allow_multiple, allow_coerce):
    if isinstance(value, list):
        try:
            return [
                _check_inclusion(
                    item, allowed, schema, allow_multiple, allow_coerce
                )
                for item in value
            ]
        except (ValueError, TypeError):
            ...
    raise ValueError(f"Value '{value}' must be a {hint}")


def _check_dict(value, allowed, hint, schema, allow_multiple, allow_coerce):
    if isinstance(value, dict):
        try:
            return {
                key: _check_inclusion(
                    item, allowed, schema, allow_multiple, allow_coerce
                )
                for key, item in value.items()
            }
        except (ValueError, TypeError):
            ...
    raise ValueError(f"Value '{value}' must be a {hint}")
