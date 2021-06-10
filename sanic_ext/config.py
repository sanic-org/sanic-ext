from sanic import Sanic

FALLBACK_CONFIG = {
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
