import pytest

from sanic import Sanic

from .utils import get_spec


@pytest.fixture
def multi_method_app(app: Sanic):
    @app.route("/ping", methods=["GET", "POST"])
    async def ping(_): ...

    return app


def test_multi_method_routes_have_unique_operation_ids(multi_method_app):
    """Each method sharing a handler gets its own operation (see #290).

    Methods are also processed in sorted order so the generated ids are
    deterministic across runs.
    """
    spec = get_spec(multi_method_app)
    get_op = spec["paths"]["/ping"]["get"]
    post_op = spec["paths"]["/ping"]["post"]
    assert get_op["operationId"] == "get~ping"
    assert post_op["operationId"] == "post~ping"
