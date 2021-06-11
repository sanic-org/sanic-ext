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
}


def add_fallback_config(app: Sanic) -> None:
    for key, value in FALLBACK_CONFIG.items():
        if key not in app.config:
            app.config[key] = value

    if isinstance(app.config.TRACE_EXCLUDED_HEADERS, str):
        app.config.TRACE_EXCLUDED_HEADERS = tuple(
            app.config.TRACE_EXCLUDED_HEADERS.split(",")
        )
