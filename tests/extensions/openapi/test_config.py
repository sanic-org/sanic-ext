import pytest

from .utils import get_spec


@pytest.mark.parametrize(
    "schemes,expected",
    (
        (None, ("http://example.com/",)),
        ("https", ("https://example.com/",)),
        (
            "http,https",
            (
                "http://example.com/",
                "https://example.com/",
            ),
        ),
        (
            ["http", "https"],
            (
                "http://example.com/",
                "https://example.com/",
            ),
        ),
    ),
)
def test_config_scheme(app, schemes, expected):
    app.config.API_SCHEMES = schemes
    app.config.API_HOST = "example.com"

    spec = get_spec(app)
    urls = {s["url"] for s in spec["servers"]}

    assert urls == set(expected)
