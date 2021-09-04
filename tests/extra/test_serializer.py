from sanic import text
from sanic.response import json

from sanic_ext import serializer


def test_serializer_with_builtin(app):
    @app.get("/")
    @serializer(text)
    async def handler(request):
        return "hello"

    @app.get("/201")
    @serializer(text, status=201)
    async def handler_201(request):
        return "hello"

    _, response = app.test_client.get("/")
    assert response.status_code == 200
    assert response.text == "hello"
    assert response.content_type == "text/plain; charset=utf-8"

    _, response = app.test_client.get("/201")
    assert response.status_code == 201
    assert response.content_type == "text/plain; charset=utf-8"


def test_serializer_with_custom(app):
    def custom(message, status):
        return json({"message": message}, status=status)

    @app.get("/")
    @serializer(custom)
    async def handler(request):
        return "hello"

    @app.get("/201")
    @serializer(custom, status=201)
    async def handler_201(request):
        return "hello"

    _, response = app.test_client.get("/")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json["message"] == "hello"

    _, response = app.test_client.get("/201")
    assert response.status_code == 201
    assert response.content_type == "application/json"
