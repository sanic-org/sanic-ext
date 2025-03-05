from typing import Any, get_origin, get_type_hints


def clean_data(model: type[object], data: dict[str, Any]) -> dict[str, Any]:
    hints = get_type_hints(model)
    return {key: _coerce(hints[key], value) for key, value in data.items()}


def _coerce(param_type, value: Any) -> Any:
    if (
        get_origin(param_type) is list
        and isinstance(value, list)
        and len(value) == 1
    ):
        value = value[0]

    return value
