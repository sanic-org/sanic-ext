from unittest.mock import Mock

import pytest
from sanic.exceptions import SanicException
from sanic.signals import Event

from sanic_ext.config import Config
from sanic_ext.extensions.injection.injector import add_injection


def test_default_config_signal():
    config = Config()
    assert config.INJECTION_SIGNAL == Event.HTTP_ROUTING_AFTER


def test_not_allowed_signals_error():
    with pytest.raises(SanicException):
        Config(injection_signal=Event.HTTP_LIFECYCLE_REQUEST)


def test_http_routing_after_succeeds():
    Config(injection_signal=Event.HTTP_ROUTING_AFTER)


@pytest.mark.skipif(
    not hasattr(Event, "HTTP_HANDLER_BEFORE"),
    reason="Sanic version does not support HTTP_HANDLER_BEFORE",
)
def test_http_handler_before_succeeds():
    Config(injection_signal=Event.HTTP_HANDLER_BEFORE)


def test_add_injection_uses_signal_config():
    app = Mock()

    app.signal = Mock(return_value=Mock())
    app.ext.config.INJECTION_SIGNAL = "random_string"
    app.ext.config.INJECTION_PRIORITY = 99999
    add_injection(app, Mock(), Mock())

    app.signal.assert_called_once_with("random_string", priority=99999)
