from typing import Any, Callable, Dict, Type

from sanic_ext.exceptions import ValidationError

from .check import check_data


def validate_body(
    validator: Callable[[Type[Any], Dict[str, Any]], Any],
    model: Type[Any],
    body: Dict[str, Any],
) -> Any:
    try:
        return validator(model, body)
    except TypeError as e:
        raise ValidationError(
            f"Invalid request body: {model.__name__}. Error: {e}"
        )


def _validate_instance(model, body):
    return model(**body)


def _validate_annotations(model, body, schema):
    return check_data(model, body, schema)
