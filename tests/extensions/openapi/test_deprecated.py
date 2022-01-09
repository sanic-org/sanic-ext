from sanic import Request, Sanic
from sanic.response import text
from utils import get_spec

from sanic_ext import openapi


def test_deprecated(app: Sanic):
    @app.route("/test0")
    @openapi.deprecated()
    async def handler0(request: Request):
        return text("ok")

    @app.route("/test1")
    @openapi.deprecated
    async def handler1(request: Request):
        return text("ok")

    @app.route("/test2")
    @openapi.deprecated
    async def handler2(request: Request):
        """
        openapi:
        ---
        summary: This is a summary.
        deprecated: true
        """
        return text("ok")

    spec = get_spec(app)
    paths = spec["paths"]
    assert len(paths) == 3
    for i in range(3):
        assert paths[f"/test{i}"]["get"]["deprecated"]
