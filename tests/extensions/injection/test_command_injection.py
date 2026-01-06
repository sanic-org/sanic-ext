from __future__ import annotations

import os
import sys

from pathlib import Path
from unittest.mock import patch

import pytest

from sanic.__main__ import main


@pytest.fixture(scope="module", autouse=True)
def tty():
    orig = sys.stdout.isatty
    sys.stdout.isatty = lambda: False
    yield
    sys.stdout.isatty = orig


def capture(command: list[str], caplog):
    caplog.clear()
    os.chdir(Path(__file__).parent.parent.parent)
    try:
        main(command)
    except SystemExit:
        ...
    return [record.message for record in caplog.records]


def test_command_injection_simple(caplog):
    """Test basic dependency injection into a command."""
    args = ["fake.server.app", "exec", "simple_inject"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "SIMPLE_INJECT value=simple" in lines


def test_command_injection_with_cli_args(caplog):
    """Test that CLI args work alongside injected dependencies."""
    args = ["fake.server.app", "exec", "inject_with_args", "--name=test"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "INJECT_WITH_ARGS name=test value=simple" in lines


def test_command_injection_with_constructor(caplog):
    """Test injection with custom constructor."""
    args = ["fake.server.app", "exec", "inject_constructor"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "INJECT_CONSTRUCTOR url=custom://url" in lines


def test_command_injection_sync_handler(caplog):
    """Test injection works with sync command handlers."""
    args = ["fake.server.app", "exec", "sync_inject"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "SYNC_INJECT value=simple" in lines


def test_command_injection_nested_dependencies(caplog):
    """Test nested dependency resolution."""
    args = ["fake.server.app", "exec", "nested_inject"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "NESTED_INJECT has_alpha=True" in lines


def test_command_injection_named_command(caplog):
    """Test injection works with renamed commands."""
    args = ["fake.server.app", "exec", "custom_name"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "CUSTOM_NAME value=simple" in lines


def test_command_injection_optional_request_dependency(caplog):
    """Test that optional request dependencies work (without request)."""
    args = ["fake.server.app", "exec", "optional_request_inject"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "OPTIONAL_REQUEST has_beta=True request=None" in lines


def test_command_injection_request_dependency_error(caplog):
    """Test that request-dependent dependencies raise helpful error."""
    args = ["fake.server.app", "exec", "request_dep_inject"]
    with patch("sys.argv", ["sanic", *args]):
        with pytest.raises(RuntimeError, match="requires a Request object"):
            capture(args, caplog)


def test_command_no_injection(caplog):
    """Test command with no dependencies passes through correctly."""
    args = ["fake.server.app", "exec", "no_injection", "--name=hello", "--count=5"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "NO_INJECTION name=hello count=5" in lines


def test_command_constant_injection(caplog):
    """Test injection of config constants."""
    args = ["fake.server.app", "exec", "constant_inject"]
    with patch("sys.argv", ["sanic", *args]):
        lines = capture(args, caplog)
    assert "CONSTANT_INJECT value=constant_value" in lines
