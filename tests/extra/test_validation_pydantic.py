from typing import Any, List
from unittest import mock

import pydantic
import pytest

from pydantic.dataclasses import dataclass
from sanic import Request, json
from sanic.views import HTTPMethodView

from sanic_ext import validate
from sanic_ext.exceptions import ValidationError


pytestmark = pytest.mark.asyncio


SNOOPY_DATA = {"name": "Snoopy", "alter_ego": ["Flying Ace", "Joe Cool"]}
PET_LIST = [{"name": "Snoopy"}, {"name": "Brutus"}, {"name": "Pluto"}]


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


def test_validate_json_list(app):
    @dataclass
    class Pet:
        name: str

    class PetList(pydantic.RootModel[List[Pet]]):
        root: List[Pet] = pydantic.Field(
            ...,
        )

    @app.post("/function")
    @validate(json=PetList)
    async def handler(_, body: PetList):
        return json(
            {
                "is_pet": all(isinstance(p, Pet) for p in body.root),
                "pets": [{"name": p.name} for p in body.root],
            }
        )

    class MethodView(HTTPMethodView, attach=app, uri="/method"):
        decorators = [validate(json=PetList)]

        async def post(self, _, body: PetList):
            return json(
                {
                    "is_pet": all(isinstance(p, Pet) for p in body.root),
                    "pets": [{"name": p.name} for p in body.root],
                }
            )

    _, response = app.test_client.post("/function", json=PET_LIST)
    assert response.status == 200
    assert response.json["is_pet"]
    assert response.json["pets"] == PET_LIST

    _, response = app.test_client.post("/method", json=PET_LIST)
    assert response.status == 200
    assert response.json["is_pet"]
    assert response.json["pets"] == PET_LIST


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
    @dataclass()
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


def test_validate_query_basemodel_ignore_extra(app):
    class Search(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="ignore")
        q: str

    @app.get("/function")
    @validate(query=Search)
    async def handler(_, query: Search):
        return json({"q": query.q, "is_search": isinstance(query, Search)})

    class MethodView(HTTPMethodView, attach=app, uri="/method"):
        decorators = [validate(query=Search)]

        async def get(self, _, query: Search):
            return json({"q": query.q, "is_search": isinstance(query, Search)})

    _, response = app.test_client.get(
        "/function", params={"q": "Snoopy", "extra_param": "extra value"}
    )
    assert response.status == 200
    assert response.json["is_search"]
    assert response.json["q"] == "Snoopy"

    _, response = app.test_client.get(
        "/method", params={"q": "Snoopy", "extra_param": "extra value"}
    )
    assert response.status == 200
    assert response.json["is_search"]
    assert response.json["q"] == "Snoopy"


def test_validate_query_basemodel_forbid_extra(app):
    class Search(pydantic.BaseModel):
        model_config = pydantic.ConfigDict(extra="forbid")
        q: str

    @app.get("/function")
    @validate(query=Search)
    async def handler(_, query: Search):
        return json({"q": query.q, "is_search": isinstance(query, Search)})

    class MethodView(HTTPMethodView, attach=app, uri="/method"):
        decorators = [validate(query=Search)]

        async def get(self, _, query: Search):
            return json({"q": query.q, "is_search": isinstance(query, Search)})

    _, response = app.test_client.get(
        "/function", params={"q": "Snoopy", "extra_param": "extra value"}
    )
    assert response.status == 400
    assert "Extra inputs are not permitted" in response.json["message"]

    _, response = app.test_client.get(
        "/method", params={"q": "Snoopy", "extra_param": "extra value"}
    )
    assert response.status == 400
    assert "Extra inputs are not permitted" in response.text


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


def test_validate_query_coerces_string_to_int(app):
    """Test that query coerces string to int."""

    class SearchQuery(pydantic.BaseModel):
        q: str
        limit: int

    @app.get("/search")
    @validate(query=SearchQuery)
    async def handler(_, query: SearchQuery):
        return json(
            {
                "q": query.q,
                "limit": query.limit,
                "limit_type": type(query.limit).__name__,
            }
        )

    _, response = app.test_client.get(
        "/search", params={"q": "test", "limit": "100"}
    )
    assert response.status == 200
    assert response.json["q"] == "test"
    assert response.json["limit"] == 100
    assert response.json["limit_type"] == "int"


def test_validate_query_with_invalid_value(app):
    """Test that lax mode still rejects completely invalid values."""

    class SearchQuery(pydantic.BaseModel):
        limit: int

    @app.get("/search")
    @validate(query=SearchQuery)
    async def handler(_, query: SearchQuery):
        return json({"limit": query.limit})

    # "abc" cannot be coerced to int even in lax mode
    _, response = app.test_client.get("/search", params={"limit": "abc"})
    assert response.status == 400


def test_validate_json_strict_mode_rejects_string_for_int(app):
    """Test that strict mode (default) rejects string values for int fields."""

    class Data(pydantic.BaseModel):
        count: int

    @app.post("/data")
    @validate(json=Data, strict=True)
    async def handler(_, body: Data):
        return json({"count": body.count})

    _, response = app.test_client.post("/data", json={"count": "100"})
    assert response.status == 400


def test_validate_json_lax_mode_coerces_string_to_int(app):
    """Test that lax mode (strict=False) coerces string to int."""

    class Data(pydantic.BaseModel):
        count: int

    @app.post("/data")
    @validate(json=Data)
    async def handler(_, body: Data):
        return json(
            {"count": body.count, "count_type": type(body.count).__name__}
        )

    _, response = app.test_client.post("/data", json={"count": "100"})
    assert response.status == 200
    assert response.json["count"] == 100
    assert response.json["count_type"] == "int"


def test_validate_query_with_float(app):
    """Test that query mode coerces string to float."""

    class SearchQuery(pydantic.BaseModel):
        price: float

    @app.get("/search")
    @validate(query=SearchQuery)
    async def handler(_, query: SearchQuery):
        return json(
            {"price": query.price, "price_type": type(query.price).__name__}
        )

    _, response = app.test_client.get("/search", params={"price": "19.99"})
    assert response.status == 200
    assert response.json["price"] == 19.99
    assert response.json["price_type"] == "float"


def test_validate_query_with_bool(app):
    """Test that query mode coerces string to bool."""

    class SearchQuery(pydantic.BaseModel):
        active: bool

    @app.get("/search")
    @validate(query=SearchQuery)
    async def handler(_, query: SearchQuery):
        return json(
            {
                "active": query.active,
                "active_type": type(query.active).__name__,
            }
        )

    # msgspec lax mode accepts "true"/"false" strings for bool
    _, response = app.test_client.get("/search", params={"active": "true"})
    assert response.status == 200
    assert response.json["active"] is True
    assert response.json["active_type"] == "bool"


def test_validate_combined_query_lax_body_strict(app):
    """Test that query_strict and body_strict can be set independently."""

    class QueryParams(pydantic.BaseModel):
        page: int

    class BodyData(pydantic.BaseModel):
        count: int

    @app.post("/data")
    @validate(query=QueryParams, json=BodyData, strict=True)
    async def handler(_, query: QueryParams, body: BodyData):
        return json({"page": query.page, "count": body.count})

    # Query with string that gets coerced, body with proper int
    _, response = app.test_client.post(
        "/data", params={"page": "5"}, json={"count": 10}
    )
    assert response.status == 200
    assert response.json["page"] == 5
    assert response.json["count"] == 10

    # Query with string that gets coerced, but body has string (should fail)
    _, response = app.test_client.post(
        "/data", params={"page": "5"}, json={"count": "10"}
    )
    assert response.status == 400
