from sanic import Request, text


class Foo:
    def bar(self):
        return "foobar"


def test_dependency_added(app):
    foo = Foo()
    foobar = Foo()

    app.ext.dependency(foo)
    app.ext.dependency(foobar, name="something")

    assert app.ctx._dependencies.foo is foo
    assert app.ctx._dependencies.something is foobar


def test_dependency_injection(app):
    foo = Foo()

    app.ext.dependency(foo)

    @app.get("/getfoo")
    async def getfoo(request: Request, foo: Foo):
        return text(foo.bar())

    _, response = app.test_client.get("/getfoo")

    assert response.text == "foobar"


def test_dependency_injection_head(app):
    foo = Foo()

    app.ext.dependency(foo)

    @app.get("/getfoo")
    async def getfoo(request: Request, foo: Foo):
        return text(foo.bar())

    _, response = app.test_client.head("/getfoo")

    assert int(response.headers.get("content-length", 0)) == 6
