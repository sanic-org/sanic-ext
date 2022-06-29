from dataclasses import dataclass

from sanic import Request, Sanic
from sanic.response import text

from sanic_ext import openapi
from sanic_ext.extensions.openapi.definitions import RequestBody

from .utils import get_spec


@dataclass
class UserProfile:
    name: str
    age: int
    email: str


def test_body(app: Sanic):
    @app.route("/test0")
    async def handler0(request: Request):
        """
        openapi:
        ---
        summary: Updates a pet in the store with form data
        description: some description
        operationId: someId
        requestBody:
          description: user to add to the system
          required: true
          content:
            application/json:
              schema:
                type: object
                required:
                  - name
                  - age
                  - email
                properties:
                  name:
                    type: string
                  email:
                    type: string
                  age:
                    type: integer
                    format: int32
                    minimum: 0
        """
        return text("ok")

    @app.route("/test1")
    @openapi.body({"application/json": UserProfile})
    async def handler1(request: Request):
        return text("ok")

    @app.route("/test2")
    @openapi.body(RequestBody({"application/json": UserProfile}))
    async def handler2(request: Request):
        return text("ok")

    @app.route("/test3")
    @openapi.body(RequestBody(UserProfile))
    async def handler3(request: Request):
        return text("ok")

    @app.route("/test4")
    @openapi.body(UserProfile)
    async def handler4(request: Request):
        return text("ok")

    spec = get_spec(app)
    for i in range(5):
        assert f"/test{i}" in spec["paths"]
        content = spec["paths"][f"/test{i}"]["get"]["requestBody"]["content"]
        media_type = next(iter(content.keys()))
        if i <= 2:
            assert media_type == "application/json"
        else:
            assert media_type == "*/*"
        properties = content[media_type]["schema"]["properties"]
        assert properties["name"]["type"] == "string"
        assert properties["age"]["type"] == "integer"
        assert properties["email"]["type"] == "string"
