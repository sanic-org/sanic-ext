from sanic import Request, Sanic, text

from sanic_ext.extensions.openapi import openapi
from sanic_ext.extensions.openapi.definitions import Parameter


def test_parameter_docstring(app: Sanic):
    DESCRIPTION = "val1 path param"

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
            name="val1", schema=int, location="path", description=DESCRIPTION
        )
    )
    async def handler2(request: Request, val1: int):
        return text("ok")

    @app.route("/test3/<val1>")
    @openapi.parameter(
        "val1", description=DESCRIPTION, required=True, schema=int
    )
    async def handler3(request: Request, val1: int):
        return text("ok")

    test_client = app.test_client
    _, response = test_client.get("/docs/openapi.json")
    paths = response.json.get("paths")
    print(paths)
    assert paths

    assert (
        paths["/test1/{val1}"]["get"]["parameters"][0]["description"]
        == DESCRIPTION
    )

    assert (
        paths["/test2/{val1}"]["get"]["parameters"][0]["description"]
        == DESCRIPTION
    )
    assert (
        paths["/test3/{val1}"]["get"]["parameters"][0]["description"]
        == DESCRIPTION
    )
