from dataclasses import dataclass
from typing import List, Optional

import pytest
from sanic_ext.extras.validation.check import check_data
from sanic_ext.extras.validation.schema import make_schema, parse_hint


def test_schema():
    @dataclass
    class Pet:
        name: str

    @dataclass
    class Person:
        name: str
        age: int
        pets: Optional[List[Pet]]

    schema = make_schema({}, Person)

    assert "Person" in schema
    assert schema["Person"]["hints"]["name"] == parse_hint(str)
    assert schema["Person"]["hints"]["age"] == parse_hint(int)
    assert schema["Person"]["hints"]["pets"] == parse_hint(Optional[List[Pet]])

    assert "Pet" in schema
    assert schema["Pet"]["hints"]["name"] == parse_hint(str)


def test_should_hydrate():
    @dataclass
    class Pet:
        name: str

    @dataclass
    class Person:
        name: str
        age: int
        pets: List[Pet]

    data = {"name": "Charlie Brown", "age": 8, "pets": [{"name": "Snoopy"}]}

    schema = make_schema({}, Person)
    cb = check_data(Person, data, schema)

    assert cb.name == "Charlie Brown"
    assert cb.age == 8
    assert cb.pets[0].name == "Snoopy"


@pytest.mark.parametrize(
    "data",
    (
        {"name": "Charlie Brown", "age": 8, "pets": {"name": "Snoopy"}},
        {"name": "Charlie Brown", "age": 8, "pets": [{"name": 123}]},
        {"name": "Charlie Brown", "age": 8, "pets": [123]},
        {"name": "Charlie Brown", "age": 8, "pets": 123},
        {"name": "Charlie Brown", "age": "8", "pets": {"name": "Snoopy"}},
        {"name": True, "age": 8, "pets": {"name": "Snoopy"}},
    ),
)
def test_should_not_hydrate(data):
    @dataclass
    class Pet:
        name: str

    @dataclass
    class Person:
        name: str
        age: int
        pets: List[Pet]

    schema = make_schema({}, Person)
    with pytest.raises(TypeError):
        check_data(Person, data, schema)
