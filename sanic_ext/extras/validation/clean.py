from typing import Any, Optional, Type, get_origin, get_type_hints

import pydantic


def clean_data(
    model: type[object],
    data: dict[str, Any],
) -> dict[str, Any]:
    if isinstance(model, pydantic.BaseModel):
        hints: dict[str, type] = {}
        for key, field in model.__annotations__.items():
            hints[key] = field.annotation
            if alias := (
                getattr(field, "validation_alias", None)
                or getattr(field, "alias", None)
            ):
                hints[alias] = field.annotation
        hints = {
            key: field.annotation
            for key, field in model.__annotations__.items()
        }
    else:
        hints = get_type_hints(model)
    return {
        key: _coerce(hints.get(key, None), value)
        for key, value in data.items()
    }


def _coerce(param_type: Optional[Type], value: Any) -> Any:
    if (
        get_origin(param_type) is not list
        and isinstance(value, list)
        and len(value) == 1
    ):
        value = value[0]

    return value
