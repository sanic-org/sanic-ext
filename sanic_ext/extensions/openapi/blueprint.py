import inspect
from os.path import abspath, dirname, realpath

from sanic.blueprints import Blueprint
from sanic.response import html, json
from sanic_ext.extensions.openapi.builders import (
    OperationStore,
    SpecificationBuilder,
)

from .utils import get_all_routes, get_blueprinted_routes

DEFAULT_SWAGGER_UI_CONFIG = {
    "apisSorter": "alpha",
    "operationsSorter": "alpha",
}


def blueprint_factory():
    oas3_blueprint = Blueprint("openapi", url_prefix="/docs")

    dir_path = dirname(realpath(__file__))
    dir_path = abspath(dir_path + "/ui")

    @oas3_blueprint.route("")
    def index(request):
        with open(dir_path + "/redoc.html", "r") as f:
            page = f.read()
        return html(page)

    @oas3_blueprint.route("/openapi.json")
    def spec(request):
        return json(SpecificationBuilder().build().serialize())

    @oas3_blueprint.route("/openapi-config")
    def config(request):
        return json(
            getattr(
                request.app.config,
                "SWAGGER_UI_CONFIGURATION",
                DEFAULT_SWAGGER_UI_CONFIG,
            )
        )

    @oas3_blueprint.listener("before_server_start")
    def build_spec(app, loop):
        specification = SpecificationBuilder()
        # --------------------------------------------------------------- #
        # Blueprint Tags
        # --------------------------------------------------------------- #

        for blueprint_name, handler in get_blueprinted_routes(app):
            operation = OperationStore()[handler]
            if not operation.tags:
                operation.tag(blueprint_name)

        # --------------------------------------------------------------- #
        # Operations
        # --------------------------------------------------------------- #
        for (
            uri,
            route_name,
            route_parameters,
            method_handlers,
        ) in get_all_routes(app, oas3_blueprint.url_prefix):

            # --------------------------------------------------------------- #
            # Methods
            # --------------------------------------------------------------- #

            uri = uri if uri == "/" else uri.rstrip("/")

            for method, _handler in method_handlers:

                if method == "OPTIONS":
                    continue

                if hasattr(_handler, "view_class"):
                    _handler = getattr(_handler.view_class, method.lower())
                operation = OperationStore()[_handler]

                if operation._exclude:
                    continue

                docstring = inspect.getdoc(_handler)

                if docstring:
                    operation.autodoc(docstring)

                if not hasattr(operation, "operationId"):
                    operation.operationId = "%s_%s" % (
                        method.lower(),
                        route_name,
                    )

                for _parameter in route_parameters:
                    operation.parameter(
                        _parameter.name, _parameter.cast, "path"
                    )

                specification.operation(uri, method, operation)

        add_static_info_to_spec_from_config(app, specification)

    return oas3_blueprint


def add_static_info_to_spec_from_config(app, specification):
    """
    Reads app.config and sets attributes to specification according to the
    desired values.

    Modifies specification in-place and returns None
    """
    specification._do_describe(
        getattr(app.config, "API_TITLE", "API"),
        getattr(app.config, "API_VERSION", "1.0.0"),
        getattr(app.config, "API_DESCRIPTION", None),
        getattr(app.config, "API_TERMS_OF_SERVICE", None),
    )

    specification._do_license(
        getattr(app.config, "API_LICENSE_NAME", None),
        getattr(app.config, "API_LICENSE_URL", None),
    )

    specification._do_contact(
        getattr(app.config, "API_CONTACT_NAME", None),
        getattr(app.config, "API_CONTACT_URL", None),
        getattr(app.config, "API_CONTACT_EMAIL", None),
    )

    for scheme in getattr(app.config, "API_SCHEMES", ["http"]):
        host = getattr(app.config, "API_HOST", None)
        basePath = getattr(app.config, "API_BASEPATH", "")
        if host is None or basePath is None:
            continue

        specification.url(f"{scheme}://{host}/{basePath}")
