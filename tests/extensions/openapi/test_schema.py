from sys import version_info
from typing import List

import pytest

from sanic_ext.extensions.openapi.types import Schema


@pytest.mark.skipif(version_info < (3, 9), reason="Not needed on 3.8")
def test_schema_list():
    class Foo:
        list1: List[int]
        list2: list[int]

        def no_show(self) -> None:
            ...

        @property
        def show(self) -> bool:
            return True

    schema = Schema.make(Foo)
    serialized = schema.serialize()
    assert "no_show" not in serialized
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
