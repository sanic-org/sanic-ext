from typing import Type, Union
from unittest.mock import Mock

import pytest
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


@pytest.mark.parametrize("instance", (True, False))
def test_multiple_extensions_pre_register(bare_app: Sanic, instance: bool):
    mock = Mock()

    class FooExtension(Extension):
        name = "foo"

        def startup(self, _) -> None:
            mock()

    class BarExtension(Extension):
        name = "bar"

        def startup(self, _) -> None:
            mock()

    foo: Union[Type[Extension], Extension] = FooExtension
    bar: Union[Type[Extension], Extension] = BarExtension
    if instance:
        foo = foo()  # type: ignore
        bar = bar()  # type: ignore

    Extend.register(foo)
    Extend.register(bar)
    bare_app.extend()

    assert mock.call_count == 2
