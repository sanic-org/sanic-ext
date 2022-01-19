from typing import List

from sanic_ext.extensions.openapi.types import Schema


class Foo:
    list1: List[int]
    list2: list[int]


def test_schema_list():
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
