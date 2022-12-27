from dataclasses import dataclass, field

import attrs
import pytest
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass as pydataclass

from sanic_ext import openapi

from .utils import get_spec


@dataclass
class FooDataclass:
    priority: int = field(
        metadata={"openapi": {"exclusiveMinimum": 1, "exclusiveMaximum": 10}}
    )
    ident: str = field(
        default="XXXX", metadata={"openapi": {"example": "ABC123"}}
    )


@attrs.define
class FooAttrs:
    priority: int = attrs.field(
        metadata={"openapi": {"exclusiveMinimum": 1, "exclusiveMaximum": 10}}
    )
    ident: str = attrs.field(
        default="XXXX", metadata={"openapi": {"example": "ABC123"}}
    )


class FooPydanticBaseModel(BaseModel):
    priority: int = Field(gt=1, lt=10)
    ident: str = Field("XXXX", example="ABC123")


@pydataclass
class FooPydanticDataclass:
    priority: int = Field(gt=1, lt=10)
    ident: str = Field("XXXX", example="ABC123")


@pytest.mark.parametrize(
    "Foo",
    (
        FooDataclass,
        FooAttrs,
        FooPydanticBaseModel,
        FooPydanticDataclass,
    ),
)
def test_pydantic_base_model(app, Foo):
    @app.get("/")
    @openapi.definition(body={"application/json": Foo})
    async def handler(_):
        ...

    spec = get_spec(app)
    foo_props = spec["paths"]["/"]["get"]["requestBody"]["content"][
        "application/json"
    ]["schema"]["properties"]

    assert foo_props["ident"] == {
        "title": "Ident",
        "type": "string",
        "default": "XXXX",
        "example": "ABC123",
    }
    assert foo_props["priority"] == {
        "title": "Priority",
        "type": "integer",
        "format": "int32",
        "exclusiveMinimum": 1,
        "exclusiveMaximum": 10,
    }
