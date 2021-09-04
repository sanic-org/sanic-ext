from functools import partial, wraps
from inspect import isawaitable, isclass
from typing import Callable, Optional, Type, Union

from sanic import Request
from sanic.log import logger

from .schema import make_schema
from .validators import (
    _validate_annotations,
    _validate_instance,
    validate_body,
)

try:
    from pydantic import BaseModel

    PYDANTIC = True
except ImportError:
    PYDANTIC = False


def validate(
    json=Optional[
        Union[
            Callable[[Request], bool],
            Type[object],
        ]
    ],
    body_argument: str = "body",
):

    schemas = (
        {
            "json": make_schema({}, json) if isclass(json) else None,
        }
        if not _is_pydantic(json)
        else {}
    )

    def decorator(f):
        @wraps(f)
        async def decorated_function(request: Request, *args, **kwargs):
            if json is not None:
                model = json
                logger.debug(f"Validating {request.path} using {model}")
                if isclass(json):
                    validator = _get_validator(model, schemas["json"])
                    validation = validate_body(validator, model, request.json)
                else:
                    validation = json(request, kwargs, request.json)
                    if isawaitable(validation):
                        await validation
                kwargs[body_argument] = validation
            retval = f(request, *args, **kwargs)
            if isawaitable(retval):
                retval = await retval
            return retval

        return decorated_function

    return decorator


def _is_pydantic(model):
    is_pydantic = PYDANTIC and (
        issubclass(model, BaseModel) or hasattr(model, "__pydantic_model__")
    )
    return is_pydantic


def _get_validator(model, schema):
    if _is_pydantic(model):
        return _validate_instance

    return partial(_validate_annotations, schema=schema)
