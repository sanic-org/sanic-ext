import pytest
from sanic import Sanic
from sanic_ext import Apply
from sanic_ext.extensions.openapi.builders import (
    OperationStore,
    SpecificationBuilder,
)


@pytest.fixture(autouse=True)
def reset_globals():
    SpecificationBuilder.reset()
    OperationStore.reset()


@pytest.fixture
def app():
    app = Sanic("ExtTesting")
    app.ctx.ext = Apply(app)

    yield app


@pytest.fixture
def get_docs(app):
    def fetch():
        nonlocal app

        _, response = app.test_client.get("/docs/openapi.json")
        return response.json

    return fetch
