from sys import version_info
from typing import List

import pytest

from sanic_ext.extensions.openapi.types import Schema


@pytest.mark.skipif(version_info < (3, 9), reason="Not needed on 3.8")
def test_schema_list():
    class Foo:
        list1: List[int]
        list2: list[int]

    schema = Schema.make(Foo)
    schema.serialize() == {
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
        },
    }
