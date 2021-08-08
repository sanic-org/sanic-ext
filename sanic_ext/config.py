from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from sanic import Sanic
from sanic.config import Config as SanicConfig

FALLBACK_CONFIG = {
    "ALL_HTTP_METHODS": True,
    "AUTO_HEAD": True,
    "AUTO_OPTIONS": True,
    "AUTO_TRACE": False,
    "CORS": True,
    "CORS_ALLOW_HEADERS": "*",
    "CORS_ALWAYS_SEND": True,
    "CORS_AUTOMATIC_OPTIONS": True,
    "CORS_EXPOSE_HEADERS": None,
    "CORS_MAX_AGE": None,
    "CORS_METHODS": None,
    "CORS_ORIGINS": "*",
    "CORS_SEND_WILDCARD": False,
    "CORS_SUPPORTS_CREDENTIALS": False,
    "CORS_VARY_HEADER": True,
    "TRACE_EXCLUDED_HEADERS": ("authorization", "cookie"),
    "OAS_URL_PREFIX": "/docs",
    "OAS_URI_TO_CONFIG": "/openapi-config",
    "OAS_URI_TO_REDOC": "/redoc",
    "OAS_URI_TO_SWAGGER": "/swagger",
    "OAS_URI_TO_JSON": "/openapi.json",
    "OAS_PATH_TO_REDOC_HTML": None,
    "OAS_PATH_TO_SWAGGER_HTML": None,
    "OAS_UI_REDOC": True,
    "OAS_UI_SWAGGER": True,
    "OAS_UI_DEFAULT": "redoc",
    "SWAGGER_UI_CONFIGURATION": {
        "apisSorter": "alpha",
        "operationsSorter": "alpha",
    },
}


class Config(SanicConfig):
    ALL_HTTP_METHODS: bool
    AUTO_HEAD: bool
    AUTO_OPTIONS: bool
    AUTO_TRACE: bool
    CORS: bool
    CORS_ALLOW_HEADERS: str
    CORS_ALWAYS_SEND: bool
    CORS_AUTOMATIC_OPTIONS: bool
    CORS_EXPOSE_HEADERS = None
    CORS_MAX_AGE = None
    CORS_METHODS = None
    CORS_ORIGINS: str
    CORS_SEND_WILDCARD: bool
    CORS_SUPPORTS_CREDENTIALS: bool
    CORS_VARY_HEADER: bool
    TRACE_EXCLUDED_HEADERS: Sequence[str]
    OAS_URL_PREFIX: str
    OAS_URI_TO_CONFIG: str
    OAS_URI_TO_REDOC: str
    OAS_URI_TO_SWAGGER: str
    OAS_URI_TO_JSON: str
    OAS_PATH_TO_REDOC_HTML: Optional[str]
    OAS_PATH_TO_SWAGGER_HTML: Optional[str]
    OAS_UI_REDOC: bool
    OAS_UI_SWAGGER: bool
    OAS_UI_DEFAULT: str
    SWAGGER_UI_CONFIGURATION: Dict[str, Any]

    def __init__(self, **kwargs):
        self.load(FALLBACK_CONFIG)
        self.load({key.upper(): value for key, value in kwargs.items()})

    @classmethod
    def from_dict(cls, mapping) -> Config:
        return cls(**mapping)


def add_fallback_config(
    app: Sanic, config: Optional[Config] = None, **kwargs
) -> Config:
    if config is None:
        config = Config(**FALLBACK_CONFIG)
    app.config.update(config)
    app.config.update(kwargs)

    if isinstance(app.config.TRACE_EXCLUDED_HEADERS, str):
        app.config.TRACE_EXCLUDED_HEADERS = tuple(
            app.config.TRACE_EXCLUDED_HEADERS.split(",")
        )

    return config
