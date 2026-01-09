from typing import Any, Callable

from sanic_ext.exceptions import ValidationError

from .check import check_data
from .clean import clean_data


try:
    from pydantic import ValidationError as PydanticValidationError

    VALIDATION_ERROR: tuple[type[Exception], ...] = (
        TypeError,
        PydanticValidationError,
    )
except ImportError:
    VALIDATION_ERROR = (TypeError,)


def validate_body(
    validator: Callable[[type[Any], dict[str, Any]], Any],
    model: type[Any],
    body: dict[str, Any],
) -> Any:
    try:
        return validator(model, body)
    except VALIDATION_ERROR as e:
        raise ValidationError(
            f"Invalid request body: {model.__name__}. Error: {e}",
            extra={"exception": str(e)},
        ) from None


def _msgspec_validate_instance(model, body, allow_coerce, strict=None):
    import msgspec

    strict = True if strict is None else strict

    try:
        data = clean_data(model, body) if allow_coerce else body
        return msgspec.convert(data, model, strict=strict)
    except msgspec.ValidationError as e:
        # Convert msgspec.ValidationError into TypeError for consistent
        # behaviour with _validate_instance
        raise TypeError(str(e))


def _validate_instance(model, body, allow_coerce, strict=None):
    strict = False if strict is None else strict
    data = clean_data(model, body) if allow_coerce else body
    if hasattr(model, "model_validate"):
        return model.model_validate(data, strict=strict)
    return model(**data)


def _validate_annotations(model, body, schema, allow_multiple, allow_coerce):
    return check_data(model, body, schema, allow_multiple, allow_coerce)
