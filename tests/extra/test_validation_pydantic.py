from unittest import mock

import pydantic

from pydantic.dataclasses import dataclass
from sanic import json, Request
from sanic.views import HTTPMethodView

from sanic_ext import validate
from sanic_ext.exceptions import ValidationError
import pytest
from typing import Any

pytestmark = pytest.mark.asyncio


SNOOPY_DATA = {"name": "Snoopy", "alter_ego": ["Flying Ace", "Joe Cool"]}


def test_validate_json(app):
    @dataclass
    class Pet:
        name: str
        alter_ego: list[str]

    @app.post("/function")
    @validate(json=Pet)
    async def handler(_, body: Pet):
        return json(
            {
                "is_pet": isinstance(body, Pet),
                "pet": {"name": body.name, "alter_ego": body.alter_ego},
            }
        )

    class MethodView(HTTPMethodView, attach=app, uri="/method"):
        decorators = [validate(json=Pet)]

        async def post(self, _, body: Pet):
            return json(
                {
                    "is_pet": isinstance(body, Pet),
                    "pet": {"name": body.name, "alter_ego": body.alter_ego},
                }
            )

    _, response = app.test_client.post("/function", json=SNOOPY_DATA)
    assert response.status == 200
    assert response.json["is_pet"]
    assert response.json["pet"] == SNOOPY_DATA

    _, response = app.test_client.post("/method", json=SNOOPY_DATA)
    assert response.status == 200
    assert response.json["is_pet"]
    assert response.json["pet"] == SNOOPY_DATA


def test_validate_form(app):
    @dataclass
    class Pet:
        name: str
        alter_ego: list[str]

    @app.post("/function")
    @validate(form=Pet)
    async def handler(_, body: Pet):
        return json(
            {
                "is_pet": isinstance(body, Pet),
                "pet": {"name": body.name, "alter_ego": body.alter_ego},
            }
        )

    class MethodView(HTTPMethodView, attach=app, uri="/method"):
        decorators = [validate(form=Pet)]

        async def post(self, _, body: Pet):
            return json(
                {
                    "is_pet": isinstance(body, Pet),
                    "pet": {"name": body.name, "alter_ego": body.alter_ego},
                }
            )

    _, response = app.test_client.post("/function", data=SNOOPY_DATA)
    assert response.status == 200
    assert response.json["is_pet"]
    assert response.json["pet"] == SNOOPY_DATA

    _, response = app.test_client.post("/method", data=SNOOPY_DATA)
    assert response.status == 200
    assert response.json["is_pet"]
    assert response.json["pet"] == SNOOPY_DATA


def test_validate_query(app):
    @dataclass
    class Search:
        q: str

    @app.get("/function")
    @validate(query=Search)
    async def handler(_, query: Search):
        return json({"q": query.q, "is_search": isinstance(query, Search)})

    class MethodView(HTTPMethodView, attach=app, uri="/method"):
        decorators = [validate(query=Search)]

        async def get(self, _, query: Search):
            return json({"q": query.q, "is_search": isinstance(query, Search)})

    _, response = app.test_client.get("/function", params={"q": "Snoopy"})
    assert response.status == 200
    assert response.json["is_search"]
    assert response.json["q"] == "Snoopy"

    _, response = app.test_client.get("/method", params={"q": "Snoopy"})
    assert response.status == 200
    assert response.json["is_search"]
    assert response.json["q"] == "Snoopy"


async def dummy_handler(request, **kwargs: dict) -> dict[str, Any]:
    return kwargs


async def test_validate_with_extra_fields_in_data():
    class Model(pydantic.BaseModel):
        a: str

    request = mock.Mock(spec=Request, args={"a": "a", "b": "b"})
    kwargs = await validate(query=Model)(dummy_handler)(request)

    assert kwargs["query"] == Model(a="a")


async def test_validate_with_aliased_fields():
    class Model(pydantic.BaseModel):
        a: str = pydantic.Field(alias="AliasedField")

    request = mock.Mock(spec=Request, args={"AliasedField": "a"})
    kwargs = await validate(query=Model)(dummy_handler)(request)

    assert kwargs["query"] == Model(AliasedField="a")


class User(pydantic.BaseModel):
    name: str
    age: int
    email: str


def test_success_validate_form_custom_message(app):
    @app.post("/user")
    @validate(form=User)
    async def create_user(request, body: User):
        return json(body.model_dump())

    user = {"name": "Alison", "age": 25, "email": "alison@almeida.com"}
    _, response = app.test_client.post("/user", data=user)
    assert response.status == 200


def test_error_validate_form_custom_message(app):
    async def server_error_validate_form(request, exception: ValidationError):
        error = exception.extra["exception"]
        return json(error, status=400)

    @app.post("/user")
    @validate(form=User)
    async def create_user(request, body: User):
        return json(body.model_dump())

    user = {"name": "Alison", "age": 25}

    app.error_handler.add(ValidationError, server_error_validate_form)
    _, response = app.test_client.post("/user", data=user)
    assert response.status == 400
