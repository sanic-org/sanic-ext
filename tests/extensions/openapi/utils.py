from typing import Dict

from sanic import Sanic


def get_spec(app: Sanic) -> Dict:
    test_client = app.test_client
    _, response = test_client.get("/docs/openapi.json")
    return response.json
