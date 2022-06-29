from sanic import Blueprint, Request, Sanic, text

from sanic_ext.extensions.openapi import openapi

from .utils import get_spec


def test_exclude_decorator(app: Sanic):
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


def test_exclude_bp(app: Sanic):
    bp1 = Blueprint("blueprint1")
    bp2 = Blueprint("blueprint2")

    @bp1.route("/op1")
    @openapi.summary("handler 1")
    async def handler1(request: Request):
        return text("bp1, ok")

    @bp2.route("/op2")
    @openapi.summary("handler 2")
    async def handler2(request: Request):
        return text("bp2, ok")

    app.blueprint(bp1)
    app.blueprint(bp2)

    openapi.exclude(bp=bp1)
    spec = get_spec(app)
    paths = spec["paths"]
    assert len(paths) == 1
    assert "/op2" in paths
    assert "/op1" not in paths
    assert paths["/op2"]["get"]["summary"] == "handler 2"
