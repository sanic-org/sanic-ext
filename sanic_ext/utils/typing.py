from typing import _GenericAlias  # type: ignore


def is_generic(item):
    return isinstance(item, _GenericAlias) or hasattr(item, "__origin__")
