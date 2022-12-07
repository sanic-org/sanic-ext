from typing import List

import attrs
from sanic import json
from sanic.views import HTTPMethodView

from sanic_ext import validate

SNOOPY_DATA = {"name": "Snoopy", "alter_ego": ["Flying Ace", "Joe Cool"]}


def test_validate_json(app):
    @attrs.define
    class Pet:
        name: str
        alter_ego: List[str]

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
    @attrs.define
    class Pet:
        name: str
        alter_ego: List[str]

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
    @attrs.define
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
