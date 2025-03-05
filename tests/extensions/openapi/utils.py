from typing import Any

from sanic import Sanic


def get_spec(app: Sanic) -> dict[str, Any]:
    test_client = app.test_client
    _, response = test_client.get("/docs/openapi.json")
    return response.json


def get_path(app: Sanic, path: str, method: str = "get") -> dict[str, Any]:
    spec = get_spec(app)
    return spec["paths"][path][method.lower()]
