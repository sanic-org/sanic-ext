from unittest.mock import Mock

from sanic import Sanic

from sanic_ext import Extend, Extension


def test_multiple_extensions(bare_app: Sanic):
    mock = Mock()

    class FooExtension(Extension):
        name = "foo"

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def startup(self, _) -> None:
            mock()

    class BarExtension(Extension):
        name = "bar"

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def startup(self, _) -> None:
            mock()

    bare_app.extend(extensions=[FooExtension, BarExtension, BarExtension])

    assert mock.call_count == 2


def test_multiple_extensions_pre_register(bare_app: Sanic):
    mock = Mock()

    class FooExtension(Extension):
        name = "foo"

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def startup(self, _) -> None:
            mock()

    class BarExtension(Extension):
        name = "bar"

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def startup(self, _) -> None:
            mock()

    Extend.register(FooExtension())
    Extend.register(BarExtension())
    bare_app.extend()

    assert mock.call_count == 2
