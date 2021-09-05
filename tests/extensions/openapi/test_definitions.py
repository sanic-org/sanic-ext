from typing import Optional

import pytest

from sanic_ext.extensions.openapi.types import Definition


@pytest.fixture
def Thing():
    class Thing(Definition):
        name: str
        foo: Optional[bool]
        bar: Optional[bool]

        def __init__(self, name, foo=None, bar=None):
            super().__init__(name=name, foo=foo, bar=bar)

    return Thing


def test_serialize_null_show_by_default(Thing):
    thing = Thing(name="ok")
    serialized = thing.serialize()

    assert serialized["name"] == "ok"
    assert serialized["foo"] is None
    assert serialized["bar"] is None


def test_serialize_some_nullable(Thing):
    Thing.__nullable__ = ["foo"]
    thing = Thing(name="ok")
    serialized = thing.serialize()

    assert serialized["name"] == "ok"
    assert serialized["foo"] is None
    assert "bar" not in serialized


def test_serialize_no_nullable(Thing):
    Thing.__nullable__ = False
    thing = Thing(name="ok")
    serialized = thing.serialize()

    assert serialized["name"] == "ok"
    assert "foo" not in serialized
    assert "bar" not in serialized
