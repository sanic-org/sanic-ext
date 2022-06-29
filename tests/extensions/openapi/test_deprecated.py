from sanic import Request, Sanic
from sanic.response import text

from sanic_ext import openapi

from .utils import get_spec


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
    async def handler2(request: Request):
        """
        openapi:
        ---
        summary: This is a summary.
        deprecated: true
        """
        return text("ok")

    @app.route("/test3")
    @openapi.definition(deprecated=True)
    async def handler3(request: Request):
        return text("ok")

    spec = get_spec(app)
    paths = spec["paths"]
    assert len(paths) == 4
    for i in range(4):
        assert paths[f"/test{i}"]["get"]["deprecated"]
