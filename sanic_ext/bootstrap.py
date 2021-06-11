from sanic import Sanic, __version__
from sanic.exceptions import SanicException

from sanic_ext.config import add_fallback_config
from sanic_ext.extensions.http.cors import add_cors
from sanic_ext.extensions.http.methods import (
    add_auto_handlers,
    add_http_methods,
)
from sanic_ext.extensions.openapi import oa3bp

min_support = (21, 3, 2)


def apply(
    app: Sanic,
    all_http_methods: bool = True,
    auto_head: bool = True,
    auto_options: bool = True,
    auto_trace: bool = False,
    cors: bool = True,
) -> None:
    """
    Ingres for instantiating sanic-ext

    :param app: Sanic application
    :type app: Sanic
    """
    if not isinstance(app, Sanic):
        raise SanicException(
            f"Cannot apply SanicExt to {app.__class__.__name__}"
        )

    sanic_version = tuple(map(int, __version__.split(".")))
    if min_support < sanic_version:
        min_version = ".".join(map(str, min_support))
        raise SanicException(
            f"SanicExt only works with Sanic v{min_version} and above. "
            f"It looks like you are running {__version__}."
        )

    add_fallback_config(app)

    if all_http_methods:
        add_http_methods(app, ["CONNECT", "TRACE"])

    if auto_head or auto_options or auto_trace:
        add_auto_handlers(app, auto_head, auto_options, auto_trace)

    if cors:
        add_cors(app)

    if app.ctx.cors.automatic_options and not auto_options:
        raise SanicException(
            "Configuration mismatch. If CORS_AUTOMATIC_OPTIONS is set to "
            "True, then you must run SanicExt with "
            "apply(..., auto_options=True)."
        )

    app.blueprint(oa3bp)
