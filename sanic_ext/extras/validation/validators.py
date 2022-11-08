from typing import Any, Callable, Dict, Tuple, Type

from sanic_ext.exceptions import ValidationError

from .check import check_data

try:
    from pydantic import ValidationError as PydanticValidationError

    VALIDATION_ERROR: Tuple[Type[Exception], ...] = (
        TypeError,
        PydanticValidationError,
    )
except ImportError:
    VALIDATION_ERROR = (TypeError,)


def validate_body(
    validator: Callable[[Type[Any], Dict[str, Any]], Any],
    model: Type[Any],
    body: Dict[str, Any],
) -> Any:
    try:
        return validator(model, body)
    except VALIDATION_ERROR as e:
        raise ValidationError(
            f"Invalid request body: {model.__name__}. Error: {e}"
        )


def has_length(value):
    return hasattr(value, "__len__")


def length_is_one(value):
    return has_length(value) and len(value) == 1


def _validate_instance(model, body):
    try:
        return model(**body)
    except VALIDATION_ERROR as e:
        if any(length_is_one(v) for v in body.values()):
            return model(
                **{k: v[0] if length_is_one(v) else v for k, v in body.items()}
            )
        else:
            raise e


def _validate_annotations(model, body, schema, allow_multiple, allow_coerce):
    return check_data(model, body, schema, allow_multiple, allow_coerce)
