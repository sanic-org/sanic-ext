"""
This module provides decorators which append
documentation to OperationStore() and components created in the blueprints.

"""
from functools import wraps
from inspect import isawaitable, isclass
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

from sanic import Blueprint
from sanic.exceptions import InvalidUsage, SanicException

from sanic_ext.extensions.openapi.builders import (
    OperationStore,
    SpecificationBuilder,
)
from sanic_ext.extensions.openapi.definitions import (
    Component,
    ExternalDocumentation,
    Parameter,
    RequestBody,
    Response,
    Tag,
)
from sanic_ext.extras.validation.setup import do_validation, generate_schema

from .types import Array  # noqa
from .types import Binary  # noqa
from .types import Boolean  # noqa
from .types import Byte  # noqa
from .types import Date  # noqa
from .types import DateTime  # noqa
from .types import Double  # noqa
from .types import Email  # noqa
from .types import Float  # noqa
from .types import Integer  # noqa
from .types import Long  # noqa
from .types import Object  # noqa
from .types import Password  # noqa
from .types import String  # noqa
from .types import Time  # noqa


def _content_or_component(content):
    if isclass(content):
        spec = SpecificationBuilder()
        if spec._components["schemas"].get(content.__name__):
            content = Component(content)
    return content


def exclude(flag: bool = True, *, bp: Optional[Blueprint] = None):
    if bp:
        for route in bp.routes:
            exclude(flag)(route.handler)
        return

    def inner(func):
        OperationStore()[func].exclude(flag)
        return func

    return inner


def operation(name: str):
    def inner(func):
        OperationStore()[func].name(name)
        return func

    return inner


def summary(text: str):
    def inner(func):
        OperationStore()[func].describe(summary=text)
        return func

    return inner


def description(text: str):
    def inner(func):
        OperationStore()[func].describe(description=text)
        return func

    return inner


def document(url: Union[str, ExternalDocumentation], description: str = None):
    def inner(func):
        OperationStore()[func].document(url, description)
        return func

    return inner


def tag(*args: Union[str, Tag]):
    def inner(func):
        OperationStore()[func].tag(*args)
        return func

    return inner


def deprecated(maybe_func=None):
    def inner(func):
        OperationStore()[func].deprecate()
        return func

    return inner(maybe_func) if maybe_func else inner


def no_autodoc(maybe_func=None):
    def inner(func):
        OperationStore()[func].disable_autodoc()
        return func

    return inner(maybe_func) if maybe_func else inner


def body(
    content: Any,
    *,
    validate: bool = False,
    body_argument: str = "body",
    **kwargs,
):
    body_content = _content_or_component(content)
    params = {**kwargs}
    validation_schema = None
    if isinstance(body_content, RequestBody):
        params = {**body_content.fields}
        body_content = params.pop("content")

    if validate:
        if callable(validate):
            model = validate
        else:
            model = body_content
            validation_schema = generate_schema(body_content)

    def inner(func):
        @wraps(func)
        async def handler(request, *handler_args, **handler_kwargs):
            if validate:
                try:
                    data = request.json
                    allow_multiple = False
                    allow_coerce = False
                except InvalidUsage:
                    data = request.form
                    allow_multiple = True
                    allow_coerce = True

                await do_validation(
                    model=model,
                    data=data,
                    schema=validation_schema,
                    request=request,
                    kwargs=handler_kwargs,
                    body_argument=body_argument,
                    allow_multiple=allow_multiple,
                    allow_coerce=allow_coerce,
                )

            retval = func(request, *handler_args, **handler_kwargs)
            if isawaitable(retval):
                retval = await retval
            return retval

        if func in OperationStore():
            OperationStore()[handler] = OperationStore().pop(func)
        OperationStore()[handler].body(body_content, **params)
        return handler

    return inner


@overload
def parameter(
    parameter: Parameter,
    **kwargs,
) -> Callable:
    ...


@overload
def parameter(
    name: Optional[str],
    schema: Optional[Type],
    location: Optional[str],
    **kwargs,
) -> Callable:
    ...


def parameter(
    name=None,
    schema=None,
    location=None,
    parameter=None,
    **kwargs,
):
    if parameter:
        if name or schema or location:
            raise SanicException(
                "When using a parameter object, you cannot pass "
                "other arguments."
            )
    if not schema:
        schema = str
    if not location:
        location = "query"

    def inner(func: Callable):
        if parameter:
            # Temporary solution convert in to location,
            # need to be changed later.
            fields = dict(parameter.fields)
            if "in" in fields:
                fields["location"] = fields.pop("in")
            OperationStore()[func].parameter(**fields)
        else:
            OperationStore()[func].parameter(name, schema, location, **kwargs)
        return func

    return inner


def response(
    status: Optional[int] = None,
    content: Optional[Any] = None,
    description: Optional[str] = None,
    *,
    response: Optional[Response] = None,
    **kwargs,
):
    if response:
        if any(bool(item) for item in (status, content, description)):
            raise SanicException(
                "When using a response object, you cannot pass "
                "other arguments."
            )

        status = response.fields["status"]
        content = response.fields["content"]
        description = response.fields["description"]

    def inner(func):
        OperationStore()[func].response(status, content, description, **kwargs)
        return func

    return inner


def secured(*args, **kwargs):
    def inner(func):
        OperationStore()[func].secured(*args, **kwargs)
        return func

    return inner


Model = TypeVar("Model")


def component(
    model: Optional[Model] = None,
    *,
    name: Optional[str] = None,
    field: str = "schemas",
):
    def wrap(m):
        return component(m, name=name, field=field)

    if not model:
        return wrap

    params = {}
    if name:
        params["name"] = name
    if field:
        params["field"] = field
    Component(model, **params)
    return model


def definition(
    *,
    exclude: Optional[bool] = None,
    operation: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    document: Optional[Union[str, ExternalDocumentation]] = None,
    tag: Optional[Union[Union[str, Tag], Sequence[Union[str, Tag]]]] = None,
    deprecated: bool = False,
    body: Optional[Union[Dict[str, Any], RequestBody, Any]] = None,
    parameter: Optional[
        Union[
            Union[Dict[str, Any], Parameter, str],
            List[Union[Dict[str, Any], Parameter, str]],
        ]
    ] = None,
    response: Optional[
        Union[
            Union[Dict[str, Any], Response, Any],
            List[Union[Dict[str, Any], Response, Any]],
        ]
    ] = None,
    secured: Optional[Dict[str, Any]] = None,
    validate: bool = False,
    body_argument: str = "body",
):
    validation_schema = None
    body_content = None

    def inner(func):
        nonlocal validation_schema
        nonlocal body_content

        glbl = globals()

        if body:
            kwargs = {}
            content = body
            if isinstance(content, RequestBody):
                kwargs = content.fields
            elif isinstance(content, dict):
                if "content" in content:
                    kwargs = content
                else:
                    kwargs["content"] = content
            else:
                content = _content_or_component(content)
                kwargs["content"] = content

            if validate:
                kwargs["validate"] = validate
                kwargs["body_argument"] = body_argument

            func = glbl["body"](**kwargs)(func)

        if exclude is not None:
            func = glbl["exclude"](exclude)(func)

        if operation:
            func = glbl["operation"](operation)(func)

        if summary:
            func = glbl["summary"](summary)(func)

        if description:
            func = glbl["description"](description)(func)

        if document:
            kwargs = {}
            if isinstance(document, str):
                kwargs["url"] = document
            else:
                kwargs["url"] = document.fields["url"]
                kwargs["description"] = document.fields["description"]

            func = glbl["document"](**kwargs)(func)

        if tag:
            taglist = []
            op = (
                "extend"
                if isinstance(tag, (list, tuple, set, frozenset))
                else "append"
            )

            getattr(taglist, op)(tag)
            func = glbl["tag"](*taglist)(func)

        if deprecated:
            func = glbl["deprecated"]()(func)

        if parameter:
            paramlist = []
            op = (
                "extend"
                if isinstance(parameter, (list, tuple, set, frozenset))
                else "append"
            )
            getattr(paramlist, op)(parameter)

            for param in paramlist:
                kwargs = {}
                if isinstance(param, Parameter):
                    kwargs = param.fields
                    if "in" in kwargs:
                        kwargs["location"] = kwargs.pop("in")
                elif isinstance(param, dict) and "name" in param:
                    kwargs = param
                elif isinstance(param, str):
                    kwargs["name"] = param
                else:
                    raise SanicException(
                        "parameter must be a Parameter instance, a string, or "
                        "a dictionary containing at least 'name'."
                    )

                if "schema" not in kwargs:
                    kwargs["schema"] = str

                func = glbl["parameter"](**kwargs)(func)

        if response:
            resplist = []
            op = (
                "extend"
                if isinstance(response, (list, tuple, set, frozenset))
                else "append"
            )
            getattr(resplist, op)(response)

            for resp in resplist:
                kwargs = {}
                if isinstance(resp, Response):
                    kwargs = resp.fields
                elif isinstance(resp, dict):
                    if "content" in resp:
                        kwargs = resp
                    else:
                        kwargs["content"] = resp
                else:
                    kwargs["content"] = resp

                if "status" not in kwargs:
                    kwargs["status"] = 200

                func = glbl["response"](**kwargs)(func)

        if secured:
            func = glbl["secured"](secured)(func)

        return func

    return inner
