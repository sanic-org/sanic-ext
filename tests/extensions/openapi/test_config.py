import pytest

from sanic import Sanic

from .utils import get_spec


def test_custom_uri_to_json():
    """Test that OAS_URI_TO_JSON is respected."""
    app = Sanic("test_custom_uri_to_json")
    app.config.OAS_URI_TO_JSON = "/custom-spec.json"
    app.extend()

    @app.get("/")
    async def handler(_): ...

    _, response = app.test_client.get("/docs/custom-spec.json")
    assert response.status == 200
    assert "openapi" in response.json


def test_custom_uri_to_json_with_leading_slash():
    """Test that leading slashes are stripped properly."""
    app = Sanic("test_custom_uri_to_json_with_leading_slash")
    app.config.OAS_URI_TO_JSON = "/my-api-spec.json"
    app.extend()

    @app.get("/")
    async def handler(_): ...

    # Verify the spec endpoint works
    _, response = app.test_client.get("/docs/my-api-spec.json")
    assert response.status == 200

    # Verify swagger UI references the correct URL
    _, response = app.test_client.get("/docs/swagger")
    assert response.status == 200
    assert "/docs/my-api-spec.json" in response.text


def test_custom_uri_to_config():
    """Test that OAS_URI_TO_CONFIG is respected in swagger UI."""
    app = Sanic("test_custom_uri_to_config")
    app.config.OAS_URI_TO_CONFIG = "/my-swagger-config"
    app.extend()

    @app.get("/")
    async def handler(_): ...

    _, response = app.test_client.get("/docs/my-swagger-config")
    assert response.status == 200

    # Verify swagger UI references the correct config URL
    _, response = app.test_client.get("/docs/swagger")
    assert response.status == 200
    assert "/docs/my-swagger-config" in response.text


def test_uri_without_leading_slash():
    """Test URIs work with or without leading slashes."""
    app = Sanic("test_uri_without_leading_slash")
    app.config.OAS_URI_TO_JSON = "spec.json"  # No leading slash
    app.extend()

    @app.get("/")
    async def handler(_): ...

    _, response = app.test_client.get("/docs/spec.json")
    assert response.status == 200
    assert "openapi" in response.json


def test_custom_swagger_cdn_url():
    """Test that OAS_UI_SWAGGER_CDN_URL is respected."""
    app = Sanic("test_custom_swagger_cdn_url")
    app.config.OAS_UI_SWAGGER_CDN_URL = "https://my-cdn.example.com/swagger-ui"
    app.extend()

    @app.get("/")
    async def handler(_): ...

    _, response = app.test_client.get("/docs/swagger")
    assert response.status == 200
    assert "https://my-cdn.example.com/swagger-ui" in response.text
    # Verify default CDN is not present
    assert "cdnjs.cloudflare.com" not in response.text


def test_custom_redoc_cdn_url():
    """Test that OAS_UI_REDOC_CDN_URL is respected."""
    app = Sanic("test_custom_redoc_cdn_url")
    app.config.OAS_UI_REDOC_CDN_URL = "https://my-cdn.example.com/redoc.js"
    app.extend()

    @app.get("/")
    async def handler(_): ...

    _, response = app.test_client.get("/docs/redoc")
    assert response.status == 200
    assert "https://my-cdn.example.com/redoc.js" in response.text
    # Verify default CDN is not present
    assert "cdn.redoc.ly" not in response.text


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
