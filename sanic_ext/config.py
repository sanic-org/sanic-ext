from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from sanic import Sanic
from sanic.config import Config as SanicConfig


class Config(SanicConfig):
    def __init__(
        self,
        all_http_methods: bool = True,
        auto_head: bool = True,
        auto_options: bool = True,
        auto_trace: bool = False,
        cors_allow_headers: str = "*",
        cors_always_send: bool = True,
        cors_automatic_options: bool = True,
        cors_expose_headers: str = None,
        cors_max_age: int = None,
        cors_methods: str = None,
        cors_origins: str = "*",
        cors_send_wildcard: bool = False,
        cors_supports_credentials: bool = False,
        cors_vary_header: bool = True,
        cors: bool = True,
        oas: bool = True,
        oas_ignore_options: bool = False,
        oas_path_to_redoc_html: Optional[str] = None,
        oas_path_to_swagger_html: Optional[str] = None,
        oas_ui_default: str = "redoc",
        oas_ui_redoc: bool = True,
        oas_ui_swagger: bool = True,
        oas_uri_to_config: str = "/openapi-config",
        oas_uri_to_json: str = "/openapi.json",
        oas_uri_to_redoc: str = "/redoc",
        oas_uri_to_swagger: str = "/swagger",
        oas_url_prefix: str = "/docs",
        swagger_ui_configuration: Optional[Dict[str, Any]] = None,
        trace_excluded_headers: Sequence[str] = ("authorization", "cookie"),
        **kwargs,
    ):
        self.ALL_HTTP_METHODS = all_http_methods
        self.AUTO_HEAD = auto_head
        self.AUTO_OPTIONS = auto_options
        self.AUTO_TRACE = auto_trace
        self.CORS_ALLOW_HEADERS = cors_allow_headers
        self.CORS_ALWAYS_SEND = cors_always_send
        self.CORS_AUTOMATIC_OPTIONS = cors_automatic_options
        self.CORS_EXPOSE_HEADERS = cors_expose_headers
        self.CORS_MAX_AGE = cors_max_age
        self.CORS_METHODS = cors_methods
        self.CORS_ORIGINS = cors_origins
        self.CORS_SEND_WILDCARD = cors_send_wildcard
        self.CORS_SUPPORTS_CREDENTIALS = cors_supports_credentials
        self.CORS_VARY_HEADER = cors_vary_header
        self.CORS = cors
        self.OAS = oas
        self.OAS_IGNORE_OPTIONS = oas_ignore_options
        self.OAS_PATH_TO_REDOC_HTML = oas_path_to_redoc_html
        self.OAS_PATH_TO_SWAGGER_HTML = oas_path_to_swagger_html
        self.OAS_UI_DEFAULT = oas_ui_default
        self.OAS_UI_REDOC = oas_ui_redoc
        self.OAS_UI_SWAGGER = oas_ui_swagger
        self.OAS_URI_TO_CONFIG = oas_uri_to_config
        self.OAS_URI_TO_JSON = oas_uri_to_json
        self.OAS_URI_TO_REDOC = oas_uri_to_redoc
        self.OAS_URI_TO_SWAGGER = oas_uri_to_swagger
        self.OAS_URL_PREFIX = oas_url_prefix
        self.SWAGGER_UI_CONFIGURATION = swagger_ui_configuration or {
            "apisSorter": "alpha",
            "operationsSorter": "alpha",
        }
        self.TRACE_EXCLUDED_HEADERS = trace_excluded_headers

        if isinstance(self.TRACE_EXCLUDED_HEADERS, str):
            self.TRACE_EXCLUDED_HEADERS = tuple(
                self.TRACE_EXCLUDED_HEADERS.split(",")
            )

        self.load({key.upper(): value for key, value in kwargs.items()})

    @classmethod
    def from_dict(cls, mapping) -> Config:
        return cls(**mapping)


def add_fallback_config(
    app: Sanic, config: Optional[Config] = None, **kwargs
) -> Config:
    if config is None:
        config = Config(**kwargs)

    app.config.update(
        {key: value for key, value in config.items() if key not in app.config}
    )

    return config
