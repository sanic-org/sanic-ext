from sanic import Request, Sanic, text
from utils import get_spec

from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Parameter


def test_parameter(app: Sanic):
    DESCRIPTION = "val1 path param"
    NAME = "val1"
    LOCATION = "path"
    TYPE = "integer"

    @app.route("/test1/<val1>")
    async def handler1(request: Request, val1: int):
        """
        openapi:
        ---
        operationId: get.test1
        parameters:
          - name: val1
            in: path
            description: val1 path param
            required: true
            schema:
                type: integer
                format: int32
        """
        return text("ok")

    @app.route("/test2/<val1>")
    @openapi.parameter(
        parameter=Parameter(
            name="val1",
            schema=int,
            location=LOCATION,
            description=DESCRIPTION,
            required=True,
        )
    )
    async def handler2(request: Request, val1: int):
        return text("ok")

    @app.route("/test3/<val1>")
    @openapi.parameter(
        "val1",
        description=DESCRIPTION,
        required=True,
        schema=int,
        location=LOCATION,
    )
    async def handler3(request: Request, val1: int):
        return text("ok")

    @app.route("/test4/<val1>")
    @openapi.definition(
        parameter={
            "name": "val1",
            "description": DESCRIPTION,
            "required": True,
            "schema": int,
            "location": LOCATION,
        }
    )
    async def handler4(request: Request, val1: int):
        return text("ok")

    spec = get_spec(app)
    for i in range(1, 5):
        assert f"/test{i}/{{val1}}" in spec["paths"]
        parameter = spec["paths"][f"/test{i}/{{val1}}"]["get"]["parameters"][0]
        assert parameter["name"] == NAME
        assert parameter["in"] == LOCATION
        assert parameter["required"] == True
        assert parameter["schema"]["type"] == TYPE
        assert parameter["description"] == DESCRIPTION
