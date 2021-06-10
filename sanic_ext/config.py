from sanic import Sanic

FALLBACK_CONFIG = {
    "TRACE_EXCLUDED_HEADERS": ("authorization", "cookie"),
    "CORS_ORIGINS": "*",
    "CORS_ALLOW_HEADERS": "",
    "CORS_SEND_WILDCARD": False,
    "CORS_SUPPORTS_CREDENTIALS": False,
    "CORS_VARY_HEADER": False,
    "CORS_METHODS": None,
    "CORS_MAX_AGE": None,
    "CORS_ALWAYS_SEND": False,
    "CORS_EXPOSE_HEADERS": "",
}
# CORS_ALWAYS_SEND (bool)
#     Usually, if a request doesn’t include an Origin header, the client did
#       not request CORS. This means we can ignore this request.
#     However, if this is true, a most-likely-to-be-correct value is still set.
# CORS_ORIGINS (List, str or re.Pattern)
#     The origin(s) to allow requests from. An origin configured here that matches the value of the Origin header in a preflight OPTIONS request is returned as the value of the Access-Control-Allow-Origin response header.
# CORS_SUPPORTS_CREDENTIALS (bool)
#     Allows users to make authenticated requests. If true, injects the Access-Control-Allow-Credentials header in responses. This allows cookies and credentials to be submitted across domains.
#     note:	This option cannot be used in conjunction with a “*” origin
# CORS_ALLOW_HEADERS (List or str)
#     Headers to accept from the client. Headers in the
#       Access-Control-Request-Headers request header (usually part of the
#       preflight OPTIONS request) maching headers in this list will be
#       included in the Access-Control-Allow-Headers response header.
# CORS_SEND_WILDCARD (bool)
#     If CORS_ORIGINS is "*" and this is true,
#       then the Access-Control-Allow-Origin response header’s value with
#       be "*" as well, instead of the value of the Origin request header.
# CORS_VARY_HEADER: (bool)
#     Enables or disables the injection of the Vary response header is set to Origin. This informs clients that our CORS headers are dynamic and cannot be cached.
# CORS_METHODS (List or str)
#     The method(s) which the allowed origins are allowed to access. These are included in the Access-Control-Allow-Methods response headers to the preflight OPTIONS requests.
# CORS_MAX_AGE (timedelta, int or str)
#     The maximum time for which this CORS request may be cached. This value is set as the Access-Control-Max-Age header.
# CORS_EXPOSE_HEADERS (List or str)
#     The CORS spec requires the server to give explicit permissions for the
#       client to read headers in CORS responses (via the
#       Access-Control-Expose-Headers header). This specifies the headers to
#       include in this header.


def add_fallback_config(app: Sanic) -> None:
    for key, value in FALLBACK_CONFIG.items():
        if key not in app.config:
            app.config[key] = value

    if isinstance(app.config.TRACE_EXCLUDED_HEADERS, str):
        app.config.TRACE_EXCLUDED_HEADERS = tuple(
            app.config.TRACE_EXCLUDED_HEADERS.split(",")
        )
