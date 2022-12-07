from pydantic.dataclasses import dataclass
from sanic import json
from sanic.views import HTTPMethodView

from sanic_ext import validate


def test_validate_decorator(app):
    @dataclass
    class Pet:
        name: str

    @app.post("/function")
    @validate(json=Pet)
    async def handler(_, body: Pet):
        return json({"is_pet": isinstance(body, Pet)})

    class MethodView(HTTPMethodView, attach=app, uri="/method"):
        decorators = [validate(json=Pet)]

        async def post(self, _, body: Pet):
            return json({"is_pet": isinstance(body, Pet)})

    _, response = app.test_client.post("/function", json={"name": "Snoopy"})
    assert response.status == 200
    assert response.json["is_pet"]

    _, response = app.test_client.post("/method", json={"name": "Snoopy"})
    assert response.status == 200
    assert response.json["is_pet"]


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
