from sanic import Request, Sanic
from sanic.response import text

from sanic_ext import openapi

from .utils import get_spec


def test_summary(app: Sanic):
    @app.route("/test0")
    async def handler0(request: Request):
        """This is a summary."""
        return text("ok")

    @app.route("/test1")
    @openapi.summary("This is a summary.")
    async def handler1(request: Request):
        return text("ok")

    @app.route("/test2")
    @openapi.definition(summary="This is a summary.")
    async def handler2(request: Request):
        return text("ok")

    @app.route("/test3")
    async def handler3(request: Request):
        """
        openapi:
        ---
        summary: This is a summary.
        """
        return text("ok")

    spec = get_spec(app)
    paths = spec["paths"]
    assert len(paths) == 4
    for i in range(4):
        assert paths[f"/test{i}"]["get"]["summary"] == "This is a summary."
