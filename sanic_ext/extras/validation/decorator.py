from functools import wraps
from inspect import isawaitable
from typing import Callable, Optional, Type, TypeVar, Union

from sanic import Request

from sanic_ext.exceptions import InitError
from sanic_ext.utils.extraction import extract_request

from .setup import do_validation, generate_schema


T = TypeVar("T")


def validate(
    json: Optional[Union[Callable[[Request], bool], Type[object]]] = None,
    form: Optional[Union[Callable[[Request], bool], Type[object]]] = None,
    query: Optional[Union[Callable[[Request], bool], Type[object]]] = None,
    body_argument: str = "body",
    query_argument: str = "query",
) -> Callable[[T], T]:
    schemas = {
        key: generate_schema(param)
        for key, param in (
            ("json", json),
            ("form", form),
            ("query", query),
        )
    }

    if json and form:
        raise InitError("Cannot define both a form and json route validator")

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            request = extract_request(*args)

            if schemas["json"]:
                await do_validation(
                    model=json,
                    data=request.json,
                    schema=schemas["json"],
                    request=request,
                    kwargs=kwargs,
                    body_argument=body_argument,
                    allow_multiple=False,
                    allow_coerce=False,
                )
            elif schemas["form"]:
                await do_validation(
                    model=form,
                    data=request.form,
                    schema=schemas["form"],
                    request=request,
                    kwargs=kwargs,
                    body_argument=body_argument,
                    allow_multiple=True,
                    allow_coerce=True,
                )
            if schemas["query"]:
                await do_validation(
                    model=query,
                    data=request.args,
                    schema=schemas["query"],
                    request=request,
                    kwargs=kwargs,
                    body_argument=query_argument,
                    allow_multiple=True,
                    allow_coerce=True,
                )
            retval = f(*args, **kwargs)
            if isawaitable(retval):
                retval = await retval
            return retval

        return decorated_function

    return decorator
