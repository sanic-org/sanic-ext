from typing import Any, Dict

from sanic import Sanic


def get_spec(app: Sanic) -> Dict[str, Any]:
    test_client = app.test_client
    _, response = test_client.get("/docs/openapi.json")
    return response.json


def get_path(app: Sanic, path: str, method: str = "get") -> Dict[str, Any]:
    spec = get_spec(app)
    return spec["paths"][path][method.lower()]
