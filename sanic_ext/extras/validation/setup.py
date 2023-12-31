from functools import partial
from inspect import isawaitable, isclass

from sanic.log import logger

from sanic_ext.exceptions import ValidationError
from sanic_ext.utils.typing import is_msgspec, is_pydantic

from .schema import make_schema
from .validators import (
    _msgspec_validate_instance,
    _validate_annotations,
    _validate_instance,
    validate_body,
)


async def do_validation(
    *,
    model,
    data,
    schema,
    request,
    kwargs,
    body_argument,
    allow_multiple,
    allow_coerce,
):
    try:
        logger.debug(f"Validating {request.path} using {model}")
        if model is not None:
            if isclass(model):
                validator = _get_validator(
                    model, schema, allow_multiple, allow_coerce
                )
                validation = validate_body(validator, model, data)
                kwargs[body_argument] = validation
            else:
                validation = model(
                    request=request, data=data, handler_kwargs=kwargs
                )
                if isawaitable(validation):
                    await validation
    except TypeError as e:
        raise ValidationError(e)


def generate_schema(param):
    try:
        if param is None or is_msgspec(param) or is_pydantic(param):
            return param
    except TypeError:
        ...

    return make_schema({}, param) if isclass(param) else param


def _get_validator(model, schema, allow_multiple, allow_coerce):
    if is_msgspec(model):
        return partial(_msgspec_validate_instance, allow_coerce=allow_coerce)
    elif is_pydantic(model):
        return partial(_validate_instance, allow_coerce=allow_coerce)

    return partial(
        _validate_annotations,
        schema=schema,
        allow_multiple=allow_multiple,
        allow_coerce=allow_coerce,
    )
