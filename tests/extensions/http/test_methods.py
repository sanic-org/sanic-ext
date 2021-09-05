from sanic.response import empty, text

from sanic_ext.bootstrap import Extend


def test_trace_and_connect_available(app):
    @app.route("/", methods=["trace", "connect"])
    async def handler(_):
        return empty()

    _, response = app.test_client.request("", http_method="trace")
    assert response.status == 204
    _, response = app.test_client.request("", http_method="connect")
    assert response.status == 204
    _, response = app.test_client.request("", http_method="get")
    assert response.status == 405


def test_auto_head(app, get_docs):
    @app.get("/foo")
    async def foo_handler(_):
        return text("...")

    assert app.config.HTTP_AUTO_HEAD
    _, response = app.test_client.head("/foo")
    assert response.status == 200
    assert len(response.body) == 0
    assert int(response.headers["content-length"]) == 3

    schema = get_docs()
    assert "get" in schema["paths"]["/foo"]


def test_auto_options(app, get_docs):
    @app.post("/foo")
    async def foo_handler(_):
        return text("...")

    _, response = app.test_client.options("/foo")
    assert response.status == 204
    assert len(response.body) == 0
    assert "POST" in response.headers["allow"]
    assert "OPTIONS" in response.headers["allow"]

    schema = get_docs()
    assert "post" in schema["paths"]["/foo"]


def test_auto_trace(bare_app):
    Extend(bare_app, config={"http_auto_trace": True})

    @bare_app.get("/foo")
    async def foo_handler(_):
        return text("...")

    request, response = bare_app.test_client.request(
        "/foo", http_method="trace"
    )
    assert response.status == 200
    assert response.body.startswith(request.head)
