from sanic.log import logger
from sanic.request import Request

from sanic_ext.exceptions import ValidationError


def validate_body(request: Request, args, kwargs, definition):
    model = definition.get(request.content_type, definition.get("*/*", None))
    if model is None:
        raise ValidationError(
            f"Invalid request content-type: {request.content_type}"
        )

    logger.debug(f"Validating {request.path} using {model}")

    try:
        kwargs["body"] = model(**request.json)
    except TypeError as e:
        raise ValidationError(
            f"Invalid request body: {model.__name__}. Error: {e}"
        )


def validate_param(request: Request, args, kwargs, name, schema, location):
    # TODO: MVP

    model = None

    logger.debug(f"Validating {request.args} using {model}")
