from sanic import Sanic

FALLBACK_CONFIG = {
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


def add_fallback_config(app: Sanic) -> None:
    for key, value in FALLBACK_CONFIG.items():
        if key not in app.config:
            app.config[key] = value

    if isinstance(app.config.TRACE_EXCLUDED_HEADERS, str):
        app.config.TRACE_EXCLUDED_HEADERS = tuple(
            app.config.TRACE_EXCLUDED_HEADERS.split(",")
        )
