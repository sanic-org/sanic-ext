from sanic import Sanic

from .utils import get_spec


def test_operation_id_is_unique_per_method_and_deterministic(app: Sanic):
    @app.route("/ping", methods=["GET", "POST"])
    async def ping(_):
        return {"ping": "pong"}

    spec = get_spec(app)
    path = spec["paths"]["/ping"]

    assert path["get"]["operationId"] == "get~ping"
    assert path["post"]["operationId"] == "post~ping"
