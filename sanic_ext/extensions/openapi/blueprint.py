import inspect
from functools import partial
from os.path import abspath, dirname, realpath

from sanic.blueprints import Blueprint
from sanic.config import Config
from sanic.response import html, json

from sanic_ext.extensions.openapi.builders import (
    OperationStore,
    SpecificationBuilder,
)

from ...utils.route import (
    clean_route_name,
    get_all_routes,
    get_blueprinted_routes,
)


def blueprint_factory(config: Config):
    bp = Blueprint("openapi", url_prefix=config.OAS_URL_PREFIX)

    dir_path = dirname(realpath(__file__))
    dir_path = abspath(dir_path + "/ui")

    for ui in ("redoc", "swagger"):
        if getattr(config, f"OAS_UI_{ui}".upper()):
            path = getattr(config, f"OAS_PATH_TO_{ui}_HTML".upper())
            uri = getattr(config, f"OAS_URI_TO_{ui}".upper())
            version = getattr(config, f"OAS_UI_{ui}_VERSION".upper(), "")
            html_path = path if path else f"{dir_path}/{ui}.html"

            with open(html_path, "r") as f:
                page = f.read()

            def index(request, page):
                return html(
                    page.replace("__VERSION__", version).replace(
                        "__URL_PREFIX__", getattr(config, "OAS_URL_PREFIX")
                    )
                )

            bp.add_route(partial(index, page=page), uri, name=ui)
            if config.OAS_UI_DEFAULT and config.OAS_UI_DEFAULT == ui:
                bp.add_route(partial(index, page=page), "", name="index")

    @bp.get(config.OAS_URI_TO_JSON)
    def spec(request):
        return json(SpecificationBuilder().build().serialize())

    if config.OAS_UI_SWAGGER:

        @bp.get(config.OAS_URI_TO_CONFIG)
        def openapi_config(request):
            return json(request.app.config.SWAGGER_UI_CONFIGURATION)

    @bp.before_server_start
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
        ) in get_all_routes(app, bp.url_prefix):

            # --------------------------------------------------------------- #
            # Methods
            # --------------------------------------------------------------- #

            uri = uri if uri == "/" else uri.rstrip("/")

            for method, _handler in method_handlers:

                if (
                    (method == "OPTIONS" and app.config.OAS_IGNORE_OPTIONS)
                    or (method == "HEAD" and app.config.OAS_IGNORE_HEAD)
                    or method == "TRACE"
                ):
                    continue

                if hasattr(_handler, "view_class"):
                    _handler = getattr(_handler.view_class, method.lower())
                operation = OperationStore()[_handler]

                if operation._exclude or "openapi" in operation.tags:
                    continue

                docstring = inspect.getdoc(_handler)

                if (
                    docstring
                    and app.config.OAS_AUTODOC
                    and operation._allow_autodoc
                ):
                    operation.autodoc(docstring)

                operation._default[
                    "operationId"
                ] = f"{method.lower()}~{route_name}"
                operation._default["summary"] = clean_route_name(route_name)

                for _parameter in route_parameters:
                    if any(
                        (
                            param.fields["name"] == _parameter.name
                            for param in operation.parameters
                        )
                    ):
                        continue

                    kwargs = {}
                    if operation._autodoc and (
                        parameters := operation._autodoc.get("parameters")
                    ):
                        description = None
                        for param in parameters:
                            if param["name"] == _parameter.name:
                                description = param["description"]
                                break
                        if description:
                            kwargs["description"] = description

                    operation.parameter(
                        _parameter.name, _parameter.cast, "path", **kwargs
                    )

                specification.operation(uri, method, operation)

        add_static_info_to_spec_from_config(app, specification)

    return bp


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
