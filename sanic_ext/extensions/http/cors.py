import re
from dataclasses import dataclass
from datetime import timedelta
from typing import FrozenSet, Tuple

from sanic import HTTPResponse, Request, Sanic
from sanic.exceptions import SanicException

WILDCARD_PATTERN = re.compile(r".*")
ORIGIN_HEADER = "access-control-allow-origin"
ALLOW_HEADERS_HEADER = "access-control-allow-headers"
ALLOW_METHODS_HEADER = "access-control-allow-methods"
EXPOSE_HEADER = "access-control-expose-headers"
CREDENTIALS_HEADER = "access-control-allow-credentials"
REQUEST_METHOD_HEADER = "access-control-request-method"
REQUEST_HEADERS_HEADER = "access-control-request-headers"
MAX_AGE_HEADER = "access-control-max-age"
VARY_HEADER = "vary"


@dataclass(frozen=True)
class CORSSettings:
    allow_headers: FrozenSet[str]
    allowed_methods: FrozenSet[str]
    allowed_origins: Tuple[re.Pattern, ...]
    always_send: bool
    automatic_options: bool
    expose_headers: FrozenSet[str]
    max_age: str
    send_wildcard: bool
    supports_credentials: bool


def add_cors(app: Sanic) -> None:
    _setup_cors_settings(app)

    @app.on_response
    async def add_cors_headers(request, response):
        _add_origin_header(request, response)

        if ORIGIN_HEADER not in response.headers:
            return

        _add_expose_header(request, response)
        _add_credentials_header(request, response)
        _add_vary_header(request, response)

        if (
            request.app.ctx.cors.automatic_options
            and request.method == "OPTIONS"
            and request.headers.get(REQUEST_METHOD_HEADER)
        ):
            _add_allow_header(request, response)
            _add_max_age_header(request, response)
            _add_methods_header(request, response)


def _setup_cors_settings(app: Sanic) -> None:
    if app.config.CORS_ORIGINS == "*" and app.config.CORS_SUPPORTS_CREDENTIALS:
        raise SanicException(
            "Cannot use supports_credentials in conjunction with"
            "an origin string of '*'. See: "
            "http://www.w3.org/TR/cors/#resource-requests"
        )

    allow_headers = _get_allow_headers(app)
    allowed_methods = _get_allowed_methods(app)
    allowed_origins = _get_allowed_origins(app)
    expose_headers = _get_expose_headers(app)
    max_age = app.config.CORS_MAX_AGE or ""
    if isinstance(max_age, timedelta):
        max_age = str(int(max_age.total_seconds()))

    app.ctx.cors = CORSSettings(
        allow_headers=allow_headers,
        allowed_methods=allowed_methods,
        allowed_origins=allowed_origins,
        always_send=app.config.CORS_ALWAYS_SEND,
        automatic_options=app.config.CORS_AUTOMATIC_OPTIONS,
        expose_headers=expose_headers,
        max_age=max_age,
        send_wildcard=app.config.CORS_SEND_WILDCARD
        and WILDCARD_PATTERN in allowed_origins,
        supports_credentials=app.config.CORS_SUPPORTS_CREDENTIALS,
    )


def _add_origin_header(request: Request, response: HTTPResponse) -> None:
    request_origin = request.headers.get("origin")
    origin_value = ""

    if request_origin:
        if request.app.ctx.cors.send_wildcard:
            origin_value = "*"
        else:
            for pattern in request.app.ctx.cors.allowed_origins:
                if pattern.match(request_origin):
                    origin_value = request_origin
                    break
    elif request.app.ctx.cors.always_send:
        if WILDCARD_PATTERN in request.app.ctx.cors.allowed_origins:
            origin_value = "*"
        else:
            if (
                isinstance(request.app.config.CORS_ORIGINS, str)
                and "," not in request.app.config.CORS_ORIGINS
            ):
                origin_value = request.app.config.CORS_ORIGINS
            else:
                origin_value = request.app.config.get("SERVER_NAME", "")

    if origin_value:
        response.headers[ORIGIN_HEADER] = origin_value


def _add_expose_header(request: Request, response: HTTPResponse) -> None:
    with_credentials = _is_request_with_credentials(request)
    expose_headers = None
    # MDN: The value "*" only counts as a special wildcard value for requests
    # without credentials (requests without HTTP cookies or HTTP
    # authentication information). In requests with credentials, it is
    # treated as the literal header name "*" without special semantics.
    # Note that the Authorization header can't be wildcarded and always
    # needs to be listed explicitly.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers
    if not with_credentials and "*" in request.app.ctx.cors.expose_headers:
        expose_headers = ["*"]
    elif request.app.ctx.cors.expose_headers:
        expose_headers = request.app.ctx.cors.expose_headers

    if expose_headers:
        response.headers[EXPOSE_HEADER] = ",".join(expose_headers)


def _add_credentials_header(request: Request, response: HTTPResponse) -> None:
    if request.app.ctx.cors.supports_credentials:
        response.headers[CREDENTIALS_HEADER] = "true"


def _add_allow_header(request: Request, response: HTTPResponse) -> None:
    with_credentials = _is_request_with_credentials(request)
    request_headers = set(
        h.strip().lower()
        for h in request.headers.get(REQUEST_HEADERS_HEADER, "").split(",")
    )

    # MDN: The value "*" only counts as a special wildcard value for requests
    # without credentials (requests without HTTP cookies or HTTP
    # authentication information). In requests with credentials,
    # it is treated as the literal header name "*" without special semantics.
    # Note that the Authorization header can't be wildcarded and always needs
    # to be listed explicitly.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers
    if not with_credentials and "*" in request.app.ctx.cors.allow_headers:
        allow_headers = ["*"]
    else:
        allow_headers = request_headers & request.app.ctx.cors.allow_headers

    if allow_headers:
        response.headers[ALLOW_HEADERS_HEADER] = ",".join(allow_headers)


def _add_max_age_header(request: Request, response: HTTPResponse) -> None:
    if request.app.ctx.cors.max_age:
        response.headers[MAX_AGE_HEADER] = request.app.ctx.cors.max_age


def _add_methods_header(request: Request, response: HTTPResponse) -> None:
    # MDN: The value "*" only counts as a special wildcard value for requests
    # without credentials (requests without HTTP cookies or HTTP
    # authentication information). In requests with credentials, it
    # is treated as the literal method name "*" without
    # special semantics.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Methods
    methods = None
    with_credentials = _is_request_with_credentials(request)
    if not with_credentials and "*" in request.app.ctx.cors.allowed_methods:
        methods = "*"
    elif request.route:
        group = request.app.router.groups.get(request.route.parts)
        if group:
            if request.app.ctx.cors.allowed_methods:
                methods = group.methods & request.app.ctx.cors.allowed_methods
            else:
                methods = group.methods

    if methods:
        response.headers[ALLOW_METHODS_HEADER] = ",".join(methods)


def _add_vary_header(request: Request, response: HTTPResponse) -> None:
    if len(request.app.ctx.cors.allowed_origins) > 1:
        response.headers[VARY_HEADER] = "origin"


def _get_allowed_origins(app: Sanic) -> Tuple[re.Pattern, ...]:
    origins = app.config.CORS_ORIGINS

    if isinstance(origins, str):
        if origins == "*":
            origins = [WILDCARD_PATTERN]
        else:
            origins = origins.split(",")
    elif isinstance(origins, re.Pattern):
        origins = [origins]

    return tuple(
        pattern if isinstance(pattern, re.Pattern) else re.compile(pattern)
        for pattern in origins
    )


def _get_expose_headers(app: Sanic) -> FrozenSet[str]:
    expose_headers = (
        (
            app.config.CORS_EXPOSE_HEADERS
            if isinstance(
                app.config.CORS_EXPOSE_HEADERS, (list, set, frozenset, tuple)
            )
            else app.config.CORS_EXPOSE_HEADERS.split(",")
        )
        if app.config.CORS_EXPOSE_HEADERS
        else tuple()
    )
    return frozenset(header.lower() for header in expose_headers)


def _get_allow_headers(app: Sanic) -> FrozenSet[str]:
    allow_headers = (
        (
            app.config.CORS_ALLOW_HEADERS
            if isinstance(
                app.config.CORS_ALLOW_HEADERS,
                (list, set, frozenset, tuple),
            )
            else app.config.CORS_ALLOW_HEADERS.split(",")
        )
        if app.config.CORS_ALLOW_HEADERS
        else tuple()
    )
    return frozenset(header.lower() for header in allow_headers)


def _get_allowed_methods(app: Sanic) -> FrozenSet[str]:
    allowed_methods = (
        (
            app.config.CORS_METHODS
            if isinstance(
                app.config.CORS_METHODS,
                (list, set, frozenset, tuple),
            )
            else app.config.CORS_METHODS.split(",")
        )
        if app.config.CORS_METHODS
        else tuple()
    )
    return frozenset(method.lower() for method in allowed_methods)


def _is_request_with_credentials(request: Request) -> bool:
    return bool(request.headers.get("authorization") or request.cookies)
