from sys import version_info
from typing import List

import pytest

from sanic_ext.extensions.openapi.types import Schema


@pytest.mark.skipif(version_info < (3, 9), reason="Not needed on 3.8")
def test_schema_list():
    class Foo:
        list1: List[int]
        list2: list[int]

        @property
        def show(self) -> bool:
            return True

        def no_show_method(self) -> None:
            ...

        @classmethod
        def no_show_classmethod(self) -> None:
            ...

        @staticmethod
        def no_show_staticmethod() -> None:
            ...

    schema = Schema.make(Foo)
    serialized = schema.serialize()
    assert "no_show_method" not in serialized
    assert "no_show_classmethod" not in serialized
    assert "no_show_staticmethod" not in serialized
    assert serialized == {
        "type": "object",
        "properties": {
            "list1": {
                "type": "array",
                "items": {"type": "integer", "format": "int32"},
            },
            "list2": {
                "type": "array",
                "items": {"type": "integer", "format": "int32"},
            },
            "show": {"type": "boolean"},
        },
    }
