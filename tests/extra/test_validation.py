from dataclasses import dataclass
from sys import version_info
from typing import Literal, Union

import pytest
from sanic import text

from sanic_ext import validate


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
def test_literal(app, annotation):
    @dataclass
    class Spec:
        name: annotation

    @app.get("/")
    @validate(query=Spec)
    def route(_, query: Spec):
        return text(query.name)

    _, response = app.test_client.get("", params={"name": "foo"})
    assert response.text == "foo"


@pytest.mark.skipif(version_info < (3, 10), reason="Not needed on 3.10")
def test_literal_3_10(app):
    @dataclass
    class Spec:
        name: Literal["foo"] | Literal["bar"]

    @app.get("/")
    @validate(query=Spec)
    def route(_, query: Spec):
        return text(query.name)

    _, response = app.test_client.get("", params={"name": "foo"})
    assert response.text == "foo"
