from sanic import Request, Sanic, text
from utils import get_spec

from sanic_ext.extensions.openapi import openapi


def test_exclude(app: Sanic):
    @app.route("/test0")
    @openapi.exclude()
    async def handler0(request: Request):
        """
        openapi:
        ---
        summary: This is a summary.
        """
        return text("ok")

    @app.route("/test1")
    @openapi.definition(summary="This is a summary.", exclude=True)
    async def handler1(request: Request):
        return text("ok")

    spec = get_spec(app)
    paths = spec["paths"]
    assert len(paths) == 0
