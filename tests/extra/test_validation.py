from sys import version_info
from typing import Literal, Union

import pytest
from sanic import text

from sanic_ext import validate


def _dataclass_spec(annotation):
    from dataclasses import dataclass

    @dataclass
    class Spec:
        name: annotation

    return Spec


def _attrs_spec(annotation):
    import attrs

    @attrs.define
    class Spec:
        name: annotation

    return Spec


def _msgspec_spec(annotation):
    from msgspec import Struct

    class Spec(Struct):
        name: annotation

    return Spec


def _pydantic_spec(annotation):
    from pydantic.dataclasses import dataclass as pydataclass

    @pydataclass
    class Spec:
        name: annotation

    return Spec


@pytest.mark.parametrize(
    "annotation",
    (
        (
            Literal["foo"],
            Literal["foo", "bar"],
            Union[Literal["foo"], Literal["bar"]],
        )
    ),
)
@pytest.mark.parametrize(
    "spec_builder",
    (
        _dataclass_spec,
        _attrs_spec,
        _msgspec_spec,
        _pydantic_spec,
    ),
)
def test_literal(app, annotation, spec_builder):
    Spec = spec_builder(annotation)

    @app.get("/")
    @validate(query=Spec)
    def route(_, query: Spec):
        return text(query.name)

    _, response = app.test_client.get("", params={"name": "foo"})
    assert response.text == "foo"


@pytest.mark.skipif(version_info < (3, 10), reason="Not needed on 3.10")
@pytest.mark.parametrize(
    "spec_builder",
    (
        _dataclass_spec,
        _attrs_spec,
        _msgspec_spec,
        _pydantic_spec,
    ),
)
def test_literal_3_10(app, spec_builder):
    Spec = spec_builder(Literal["foo"] | Literal["bar"])

    @app.get("/")
    @validate(query=Spec)
    def route(_, query: Spec):
        return text(query.name)

    _, response = app.test_client.get("", params={"name": "foo"})
    assert response.text == "foo"
