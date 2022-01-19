import json
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import UUID

import pytest
from sanic_ext import openapi

from utils import get_path, get_spec


class Choice(Enum):
    ONE = 1
    TWO = 2


class Bar:
    name: str


class LittleFoo:
    iid: int
    bar: Bar


class BigFoo:
    iid: int
    uid: UUID
    created: date
    updated: datetime
    multi: Union[str, int]
    nullable_single: Optional[bool]
    nullable_multi: Optional[Union[str, int]]
    bar: Bar
    adict: Dict[str, Any]
    anything: Any
    choice: Choice


@pytest.mark.parametrize(
    "args,content_type",
    (
        ((LittleFoo,), "*/*"),
        (({"application/json": LittleFoo},), "application/json"),
        ((openapi.definitions.RequestBody(LittleFoo),), "*/*"),
        (
            (
                openapi.definitions.RequestBody(
                    {"application/json": LittleFoo}
                ),
            ),
            "application/json",
        ),
    ),
)
def test_body_decorator(app, args, content_type):
    @app.route("/")
    @openapi.body(*args, description="something")
    async def handler(_):
        ...

    spec = get_path(app, "/")

    assert spec["requestBody"]["description"] == "something"

    content = spec["requestBody"]["content"]

    assert content_type in content

    schema = content[content_type]["schema"]

    assert schema["type"] == "object"
    assert schema["properties"]["bar"]["type"] == "object"
    assert (
        schema["properties"]["bar"]["properties"]["name"]["type"] == "string"
    )


@pytest.mark.parametrize(
    "decorator", (openapi.deprecated(), openapi.deprecated)
)
def test_deprecated_decorator(app, decorator):
    @app.route("/")
    @decorator
    async def handler(_):
        ...

    spec = get_path(app, "/")
    assert spec["deprecated"]


def test_description_decorator(app):
    @app.route("/")
    @openapi.description("foo")
    async def handler(_):
        ...

    spec = get_path(app, "/")
    assert spec["description"] == "foo"


@pytest.mark.parametrize(
    "args",
    (
        ("http://example.com/docs",),
        (
            openapi.definitions.ExternalDocumentation(
                "http://example.com/docs"
            ),
        ),
    ),
)
def test_document_decorator(app, args):
    @app.route("/")
    @openapi.document(*args)
    async def handler(_):
        ...

    spec = get_path(app, "/")
    assert spec["externalDocs"]["url"] == "http://example.com/docs"


@pytest.mark.parametrize(
    "decorator,excluded",
    (
        (openapi.exclude(), True),
        (openapi.exclude(True), True),
        (openapi.exclude(False), False),
    ),
)
def test_exclude_decorator(app, decorator, excluded):
    @app.route("/")
    @decorator
    async def handler(_):
        ...

    if excluded:
        with pytest.raises(KeyError):
            get_path(app, "/")
    else:
        get_path(app, "/")


def test_operation_decorator(app):
    @app.route("/")
    @openapi.operation("foo")
    async def handler(_):
        ...

    spec = get_path(app, "/")
    assert spec["operationId"] == "foo"


@pytest.mark.parametrize(
    "decorator,expected",
    (
        (
            openapi.parameter("thing"),
            {
                "name": "thing",
                "schema": {"type": "string"},
                "in": "query",
            },
        ),
        (
            openapi.parameter("Authorization", str, "header"),
            {
                "name": "Authorization",
                "schema": {"type": "string"},
                "in": "header",
            },
        ),
        (
            openapi.parameter(
                parameter=openapi.definitions.Parameter(
                    "foobar", deprecated=True
                )
            ),
            {
                "name": "foobar",
                "schema": {"type": "string"},
                "deprecated": True,
                "in": "query",
            },
        ),
        (
            openapi.parameter("thing", required=True),
            {
                "name": "thing",
                "schema": {"type": "string"},
                "required": True,
                "in": "query",
            },
        ),
    ),
)
def test_parameter_decorator(app, decorator, expected):
    @app.route("/")
    @decorator
    def handler_one(_):
        ...

    parameters = get_path(app, "/")["parameters"]
    assert parameters[0] == expected


@pytest.mark.parametrize(
    "decorator,expected",
    (
        (
            openapi.response(),
            {
                "default": {
                    "content": {"*/*": {"schema": {"type": "string"}}},
                    "description": "Default Response",
                }
            },
        ),
        (
            openapi.response(200, str, "foobar"),
            {
                "200": {
                    "content": {"*/*": {"schema": {"type": "string"}}},
                    "description": "foobar",
                }
            },
        ),
        (
            openapi.response(200, Bar, "..."),
            {
                "200": {
                    "content": {
                        "*/*": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                            }
                        }
                    },
                    "description": "...",
                }
            },
        ),
        (
            openapi.response(
                content={"application/json": Bar}, description="..."
            ),
            {
                "default": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                            }
                        }
                    },
                    "description": "...",
                }
            },
        ),
        (
            openapi.response(
                response=openapi.definitions.Response(
                    {"application/json": Bar}, description="...", status=201
                )
            ),
            {
                "201": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                            }
                        }
                    },
                    "description": "...",
                }
            },
        ),
        (
            openapi.response(content={"application/json": BigFoo}),
            {
                "default": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "iid": {
                                        "type": "integer",
                                        "format": "int32",
                                    },
                                    "uid": {
                                        "type": "string",
                                        "format": "uuid",
                                    },
                                    "created": {
                                        "type": "string",
                                        "format": "date",
                                    },
                                    "updated": {
                                        "type": "string",
                                        "format": "date-time",
                                    },
                                    "multi": {
                                        "oneOf": [
                                            {"type": "string"},
                                            {
                                                "type": "integer",
                                                "format": "int32",
                                            },
                                        ]
                                    },
                                    "nullable_single": {
                                        "type": "boolean",
                                        "nullable": True,
                                    },
                                    "nullable_multi": {
                                        "nullable": True,
                                        "oneOf": [
                                            {
                                                "type": "string",
                                            },
                                            {
                                                "type": "integer",
                                                "format": "int32",
                                            },
                                        ],
                                    },
                                    "bar": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"}
                                        },
                                    },
                                    "adict": {"type": "object"},
                                    "anything": {},
                                    "choice": {
                                        "type": "integer",
                                        "format": "int32",
                                        "enum": [1, 2],
                                    },
                                },
                            }
                        }
                    },
                    "description": "Default Response",
                }
            },
        ),
    ),
)
def test_response_decorator(app, decorator, expected):
    @app.route("/")
    @decorator
    def handler_one(_):
        ...

    responses = get_path(app, "/")["responses"]
    assert responses == expected


def test_summary_decorator(app):
    @app.route("/")
    @openapi.summary("foo")
    async def handler(_):
        ...

    spec = get_path(app, "/")
    assert spec["summary"] == "foo"


# @openapi.definition(body=Foo)
# @openapi.definition(body={"application/json": Foo})
